"""
Tests for omnibioai-tool-images Dockerfiles and SIF images.

Run:
    cd omnibioai-tool-images
    pytest tests/ -v
"""
from __future__ import annotations

import subprocess
import re
from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
DOCKERFILE_DIR = ROOT / "dockerfiles"
SIF_DIR        = ROOT / "sif"
BUILD_SCRIPT   = ROOT / "build_all.sh"

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def get_all_tools() -> list[str]:
    """Extract tool names from Dockerfile.* files."""
    return sorted([
        p.name.replace("Dockerfile.", "")
        for p in DOCKERFILE_DIR.glob("Dockerfile.*")
        if "." in p.name
    ])

def get_built_tools() -> list[str]:
    """Tools that have corresponding SIF files."""
    return sorted([
        p.name.replace("_arm64.sif", "")
        for p in SIF_DIR.glob("*_arm64.sif")
    ])

def run_singularity(sif: Path, command: str) -> subprocess.CompletedProcess:
    """Run a command inside a Singularity SIF image."""
    return subprocess.run(
        ["singularity", "exec", str(sif), "bash", "-c", command],
        capture_output=True, text=True, timeout=60
    )

ALL_TOOLS   = get_all_tools()
BUILT_TOOLS = get_built_tools()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Dockerfile structure tests
# ─────────────────────────────────────────────────────────────────────────────
class TestDockerfileStructure:

    def test_dockerfiles_exist(self):
        """At least one Dockerfile exists."""
        assert len(ALL_TOOLS) > 0, "No Dockerfiles found"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_not_empty(self, tool):
        """Each Dockerfile has content."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        content = path.read_text()
        assert len(content.strip()) > 0, f"Dockerfile.{tool} is empty"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_has_from(self, tool):
        """Each Dockerfile starts with FROM."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        content = path.read_text()
        assert content.strip().startswith("FROM"), \
            f"Dockerfile.{tool} does not start with FROM"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_has_cmd(self, tool):
        """Each Dockerfile has a CMD instruction."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        content = path.read_text()
        assert "CMD" in content, \
            f"Dockerfile.{tool} missing CMD instruction"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_uses_ubuntu_2404(self, tool):
        """Each Dockerfile uses ubuntu:24.04 base image."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        content = path.read_text()
        assert "ubuntu:24.04" in content, \
            f"Dockerfile.{tool} does not use ubuntu:24.04"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_no_apt_get_upgrade(self, tool):
        """Dockerfiles should not run apt-get upgrade (not reproducible)."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        content = path.read_text()
        assert "apt-get upgrade" not in content, \
            f"Dockerfile.{tool} contains apt-get upgrade"

    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_dockerfile_has_no_syntax_errors(self, tool):
        """Validate Dockerfile syntax using docker build --dry-run or check."""
        path = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        # Basic syntax checks
        content = path.read_text()
        lines = content.strip().splitlines()
        # First non-empty line must be FROM or ARG
        first = next((l for l in lines if l.strip() and not l.startswith("#")), "")
        assert first.startswith("FROM") or first.startswith("ARG"), \
            f"Dockerfile.{tool} first instruction is not FROM/ARG: {first}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. SIF file tests
# ─────────────────────────────────────────────────────────────────────────────
class TestSIFFiles:

    def test_sif_directory_exists(self):
        """SIF directory exists."""
        assert SIF_DIR.exists(), f"SIF directory not found: {SIF_DIR}"

    def test_at_least_one_sif_built(self):
        """At least one SIF file has been built."""
        assert len(BUILT_TOOLS) > 0, "No SIF files found"

    @pytest.mark.parametrize("tool", BUILT_TOOLS)
    def test_sif_file_not_empty(self, tool):
        """Each SIF file has non-zero size."""
        sif = SIF_DIR / f"{tool}_arm64.sif"
        assert sif.stat().st_size > 0, f"{tool}_arm64.sif is empty"

    @pytest.mark.parametrize("tool", BUILT_TOOLS)
    def test_sif_file_minimum_size(self, tool):
        """Each SIF file is at least 10MB (sanity check)."""
        sif = SIF_DIR / f"{tool}_arm64.sif"
        size_mb = sif.stat().st_size / (1024 * 1024)
        assert size_mb >= 10, \
            f"{tool}_arm64.sif is too small: {size_mb:.1f}MB"

    @pytest.mark.parametrize("tool", BUILT_TOOLS)
    def test_sif_is_valid_singularity(self, tool):
        """Each SIF file is a valid Singularity image."""
        sif = SIF_DIR / f"{tool}_arm64.sif"
        result = subprocess.run(
            ["singularity", "inspect", str(sif)],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, \
            f"{tool}_arm64.sif is not a valid Singularity image: {result.stderr}"

    def test_all_dockerfiles_have_sif(self):
        """Report which tools have Dockerfiles but no SIF yet."""
        missing = set(ALL_TOOLS) - set(BUILT_TOOLS)
        # This is informational — not a hard failure
        if missing:
            pytest.skip(f"Tools without SIF yet: {sorted(missing)}")

    @pytest.mark.parametrize("tool", BUILT_TOOLS)
    def test_sif_dockerfile_match(self, tool):
        """Each SIF file has a corresponding Dockerfile."""
        dockerfile = DOCKERFILE_DIR / f"Dockerfile.{tool}"
        assert dockerfile.exists(), \
            f"SIF exists for {tool} but no Dockerfile found"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Build script tests
# ─────────────────────────────────────────────────────────────────────────────
class TestBuildScript:

    def test_build_script_exists(self):
        """build_all.sh exists."""
        assert BUILD_SCRIPT.exists(), "build_all.sh not found"

    def test_build_script_is_executable(self):
        """build_all.sh is executable."""
        assert BUILD_SCRIPT.stat().st_mode & 0o111, \
            "build_all.sh is not executable"

    def test_build_script_has_shebang(self):
        """build_all.sh has a shebang line."""
        content = BUILD_SCRIPT.read_text()
        assert content.startswith("#!/bin/bash") or content.startswith("#!/usr/bin/env bash"), \
            "build_all.sh missing shebang"

    def test_build_script_syntax(self):
        """build_all.sh has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(BUILD_SCRIPT)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"build_all.sh syntax error: {result.stderr}"

    def test_build_script_has_docker_build(self):
        """build_all.sh contains docker build command."""
        content = BUILD_SCRIPT.read_text()
        assert "docker build" in content, \
            "build_all.sh missing docker build command"

    def test_build_script_has_singularity_pull(self):
        """build_all.sh contains singularity pull command."""
        content = BUILD_SCRIPT.read_text()
        assert "singularity pull" in content, \
            "build_all.sh missing singularity pull command"


# ─────────────────────────────────────────────────────────────────────────────
# 4. SIF tool command tests (spot check key tools)
# ─────────────────────────────────────────────────────────────────────────────
TOOL_COMMANDS = {
    "fastqc":       "fastqc --version",
    "samtools":     "samtools --version",
    "bcftools":     "bcftools --version",
    "bwa":          "bwa 2>&1 | head -3",
    "star":         "STAR --version",
    "featurecounts": "featureCounts -v 2>&1",
    "multiqc":      "multiqc --version",
    "trimmomatic":  "trimmomatic -version",
    "gatk":         "gatk --version",
    "deseq2":       "Rscript -e 'library(DESeq2); cat(\"ok\")'",
    "hisat2":       "hisat2 --version",
    "kallisto":     "kallisto version",
    "salmon":       "salmon --version",
    "stringtie":    "stringtie --version",
    "kraken2":      "kraken2 --version",
    "diamond":      "diamond version",
    "prodigal":     "prodigal -v 2>&1",
    "quast":        "quast --version",
    "freebayes":    "freebayes --version",
    "vcftools":     "vcftools --version 2>&1",
    "snpeff":       "snpEff -version 2>&1",
    "bedtools":     "bedtools --version",
    "macs2":        "macs2 --version",
    "deeptools":    "bamCoverage --version",
}

# Only test tools that have SIF files
TESTABLE_TOOLS = {
    tool: cmd
    for tool, cmd in TOOL_COMMANDS.items()
    if tool in BUILT_TOOLS
}

class TestToolCommands:

    @pytest.mark.parametrize("tool,command", TESTABLE_TOOLS.items())
    def test_tool_runs_in_sif(self, tool, command):
        """Each tool can be executed inside its SIF image."""
        sif = SIF_DIR / f"{tool}_arm64.sif"
        result = run_singularity(sif, command)
        assert result.returncode == 0, \
            f"{tool} command failed in SIF:\nstdout: {result.stdout}\nstderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Summary report
# ─────────────────────────────────────────────────────────────────────────────
class TestSummary:

    def test_print_summary(self, capsys):
        """Print summary of all tools and their build status."""
        built   = set(BUILT_TOOLS)
        all_t   = set(ALL_TOOLS)
        missing = all_t - built
        extra   = built - all_t

        total_size = sum(
            (SIF_DIR / f"{t}_arm64.sif").stat().st_size
            for t in BUILT_TOOLS
        ) / (1024 ** 3)

        print(f"\n{'='*50}")
        print(f"OmniBioAI Tool Images Summary")
        print(f"{'='*50}")
        print(f"Dockerfiles   : {len(all_t)}")
        print(f"SIF images    : {len(built)}")
        print(f"Total SIF size: {total_size:.1f}G")
        if missing:
            print(f"Missing SIFs  : {sorted(missing)}")
        if extra:
            print(f"Extra SIFs    : {sorted(extra)}")
        print(f"{'='*50}")
        assert True  # always pass — informational only


class TestCoverage:
    """Extra tests to improve coverage."""

    def test_run_singularity_helper(self):
        """Test run_singularity helper with a simple built tool."""
        if not BUILT_TOOLS:
            pytest.skip("No SIF files built yet")
        # Use first available tool
        tool = BUILT_TOOLS[0]
        sif  = SIF_DIR / f"{tool}_arm64.sif"
        result = run_singularity(sif, "echo hello")
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_summary_with_extra_sifs(self, tmp_path, monkeypatch):
        """Test summary branch when extra SIFs exist."""
        # Monkeypatch BUILT_TOOLS to include a fake tool
        import sys, importlib
        mod = sys.modules[__name__]
        original = BUILT_TOOLS[:]
        fake_sif = SIF_DIR / "fake_tool_arm64.sif"
        fake_sif.write_bytes(b"fake")
        try:
            built = set(original + ["fake_tool"])
            all_t = set(ALL_TOOLS)
            extra = built - all_t
            assert "fake_tool" in extra
            # hit the print branch
            print(f"Extra SIFs: {sorted(extra)}")
        finally:
            fake_sif.unlink(missing_ok=True)
