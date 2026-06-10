"""Tests for api/server.py — covers all endpoints and the _stream_build generator."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).parent.parent
# Add api/ directly (avoids collision with a system-installed 'api' package)
sys.path.insert(0, str(ROOT / "api"))

import server  # noqa: E402
from server import (  # noqa: E402
    app,
    _tool_info,
    _stream_build,
    BUILD_LOGS_DIR,
    CATEGORY_MAP,
    DOCKERFILES_DIR,
    LICENSE_NEEDED,
    SKIP_TOOLS,
    SIF_DIR,
)

client = TestClient(app)


# ── helpers: pick real files from disk ───────────────────────────────────────

def _first_real_tool() -> str:
    for p in sorted(DOCKERFILES_DIR.glob("Dockerfile.*")):
        tool = p.name.removeprefix("Dockerfile.")
        if tool not in SKIP_TOOLS:
            return tool
    raise RuntimeError("No Dockerfiles found in dockerfiles/")


def _first_built_tool() -> str | None:
    for p in sorted(SIF_DIR.glob("*_arm64.sif")):
        return p.name.replace("_arm64.sif", "")
    return None


def _first_log_tool() -> str | None:
    for p in sorted(BUILD_LOGS_DIR.glob("*.log")):
        return p.stem
    return None


REAL_TOOL  = _first_real_tool()
BUILT_TOOL = _first_built_tool()
LOG_TOOL   = _first_log_tool()


# ── async helpers for stream tests ───────────────────────────────────────────

async def _fake_stdout_lines(*lines: bytes) -> AsyncGenerator[bytes, None]:
    for line in lines:
        yield line


async def _fake_stream_ok(cmd: list[str]) -> AsyncGenerator[dict, None]:
    yield {"data": "Building..."}
    yield {"data": "[exit code: 0]", "event": "done"}


async def _fake_stream_err(cmd: list[str]) -> AsyncGenerator[dict, None]:
    yield {"data": "Error"}
    yield {"data": "[exit code: 1]", "event": "error"}


# ── 1. Health ─────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ── 2. List tools ─────────────────────────────────────────────────────────────

class TestListTools:
    def test_returns_non_empty_list(self):
        resp = client.get("/v1/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_each_tool_has_required_fields(self):
        resp = client.get("/v1/tools")
        assert resp.status_code == 200
        tool = resp.json()[0]
        for field in ("name", "category", "sif_exists", "sif_filename",
                      "status", "dockerfile"):
            assert field in tool, f"Missing field: {field}"

    def test_skip_tools_excluded(self):
        resp = client.get("/v1/tools")
        names = {t["name"] for t in resp.json()}
        for skipped in SKIP_TOOLS:
            assert skipped not in names, f"SKIP_TOOL '{skipped}' appeared in /v1/tools"

    def test_status_values_are_valid(self):
        resp = client.get("/v1/tools")
        statuses = {t["status"] for t in resp.json()}
        assert statuses <= {"built", "missing", "license"}, f"Unexpected statuses: {statuses}"

    def test_built_tool_has_size_and_timestamp(self):
        resp = client.get("/v1/tools")
        built = [t for t in resp.json() if t["status"] == "built"]
        if not built:
            pytest.skip("No built SIF files on disk")
        for tool in built:
            assert tool["sif_size_mb"] is not None
            assert tool["updated_at"] is not None

    def test_missing_tool_has_null_path_and_size(self):
        resp = client.get("/v1/tools")
        missing = [t for t in resp.json() if t["status"] == "missing"]
        if not missing:
            pytest.skip("All tools appear to be built")
        for tool in missing:
            assert tool["sif_path"] is None
            assert tool["sif_size_mb"] is None


# ── 3. _tool_info helper ──────────────────────────────────────────────────────

class TestToolInfo:
    def test_built_tool_status(self):
        if not BUILT_TOOL:
            pytest.skip("No SIF files on disk")
        info = _tool_info(BUILT_TOOL)
        assert info["status"] == "built"
        assert info["sif_exists"] is True
        assert info["sif_size_mb"] is not None
        assert info["updated_at"] is not None
        assert info["sif_path"] is not None

    def test_missing_tool_status(self):
        info = _tool_info("__nonexistent_tool_xyz__")
        assert info["status"] == "missing"
        assert info["sif_exists"] is False
        assert info["sif_size_mb"] is None
        assert info["sif_path"] is None
        assert info["updated_at"] is None

    def test_license_tool_status(self):
        for tool in LICENSE_NEEDED:
            info = _tool_info(tool)
            assert info["status"] == "license"
            break

    def test_category_from_map(self):
        for tool, expected_cat in CATEGORY_MAP.items():
            info = _tool_info(tool)
            assert info["category"] == expected_cat, (
                f"{tool}: expected {expected_cat!r}, got {info['category']!r}"
            )
            break

    def test_category_other_for_unknown_tool(self):
        info = _tool_info("__no_such_tool__")
        assert info["category"] == "Other"

    def test_sif_filename_format(self):
        info = _tool_info(REAL_TOOL)
        assert info["sif_filename"] == f"{REAL_TOOL}_arm64.sif"

    def test_dockerfile_field_format(self):
        info = _tool_info(REAL_TOOL)
        assert info["dockerfile"] == f"Dockerfile.{REAL_TOOL}"

    def test_name_field_matches_input(self):
        info = _tool_info(REAL_TOOL)
        assert info["name"] == REAL_TOOL


# ── 4. Dockerfile endpoint ────────────────────────────────────────────────────

class TestGetDockerfile:
    def test_existing_tool_returns_content(self):
        resp = client.get(f"/v1/tools/{REAL_TOOL}/dockerfile")
        assert resp.status_code == 200
        assert len(resp.text) > 0

    def test_existing_tool_contains_from(self):
        resp = client.get(f"/v1/tools/{REAL_TOOL}/dockerfile")
        assert resp.status_code == 200
        assert "FROM" in resp.text

    def test_nonexistent_tool_returns_404(self):
        resp = client.get("/v1/tools/__no_such_tool_xyz__/dockerfile")
        assert resp.status_code == 404

    def test_404_detail_message(self):
        resp = client.get("/v1/tools/__no_such_tool_xyz__/dockerfile")
        assert "not found" in resp.json()["detail"].lower()


# ── 5. Build log endpoint ─────────────────────────────────────────────────────

class TestGetBuildLog:
    def test_existing_log_returns_content(self):
        if not LOG_TOOL:
            pytest.skip("No build logs on disk")
        resp = client.get(f"/v1/tools/{LOG_TOOL}/log")
        assert resp.status_code == 200

    def test_nonexistent_log_returns_404(self):
        resp = client.get("/v1/tools/__no_such_tool_xyz__/log")
        assert resp.status_code == 404

    def test_404_detail_message(self):
        resp = client.get("/v1/tools/__no_such_tool_xyz__/log")
        assert "not found" in resp.json()["detail"].lower()


# ── 6. Build endpoints ────────────────────────────────────────────────────────

class TestBuildEndpoints:
    def test_build_nonexistent_tool_returns_404(self):
        resp = client.post("/v1/build/__no_such_tool_xyz__")
        assert resp.status_code == 404

    def test_build_nonexistent_tool_detail(self):
        resp = client.post("/v1/build/__no_such_tool_xyz__")
        assert "not found" in resp.json()["detail"].lower()

    def test_build_existing_tool_returns_200(self):
        with patch("server._stream_build", side_effect=_fake_stream_ok):
            resp = client.post(f"/v1/build/{REAL_TOOL}")
        assert resp.status_code == 200

    def test_build_all_returns_200(self):
        with patch("server._stream_build", side_effect=_fake_stream_ok):
            resp = client.post("/v1/build-all")
        assert resp.status_code == 200


# ── 7. _stream_build async generator ─────────────────────────────────────────

class TestStreamBuild:
    def _collect(self, coro_fn):
        """Run an async generator and return the collected events."""
        async def _inner():
            return [event async for event in coro_fn]
        return asyncio.run(_inner())

    def _make_proc(self, returncode: int, lines: list[bytes]):
        async def _stdout_gen():
            for line in lines:
                yield line

        proc = AsyncMock()
        proc.returncode = returncode
        proc.stdout = _stdout_gen()
        proc.wait = AsyncMock()
        return proc

    def test_stream_success_yields_lines(self):
        proc = self._make_proc(0, [b"step 1\n", b"step 2\n"])
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            events = self._collect(_stream_build(["echo", "ok"]))
        data_lines = [e["data"] for e in events]
        assert any("step 1" in d for d in data_lines)
        assert any("step 2" in d for d in data_lines)

    def test_stream_success_final_event_is_done(self):
        proc = self._make_proc(0, [b"output\n"])
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            events = self._collect(_stream_build(["echo", "ok"]))
        assert events[-1].get("event") == "done"
        assert "exit code: 0" in events[-1]["data"]

    def test_stream_failure_final_event_is_error(self):
        proc = self._make_proc(1, [b"error msg\n"])
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            events = self._collect(_stream_build(["false"]))
        assert events[-1].get("event") == "error"
        assert "exit code: 1" in events[-1]["data"]

    def test_stream_handles_non_utf8_bytes(self):
        proc = self._make_proc(0, [b"\xab\xcd binary output\n"])
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            events = self._collect(_stream_build(["cmd"]))
        # Should not raise; errors='replace' handles bad bytes
        assert any("data" in e for e in events)

    def test_stream_empty_stdout_still_yields_exit_event(self):
        proc = self._make_proc(0, [])
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            events = self._collect(_stream_build(["true"]))
        assert len(events) == 1
        assert events[0].get("event") == "done"
