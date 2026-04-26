FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip libgomp1 wget unzip && rm -rf /var/lib/apt/lists/*
RUN wget -q https://github.com/alexdobin/STAR/releases/download/2.7.11b/STAR_2.7.11b.zip \
    -O /tmp/STAR.zip \
    && unzip -q /tmp/STAR.zip -d /tmp/STAR \
    && mv /tmp/STAR/STAR_2.7.11b/Linux_x86_64_static/STAR /usr/local/bin/STAR \
    && chmod +x /usr/local/bin/STAR \
    && rm -rf /tmp/STAR /tmp/STAR.zip
RUN pip3 install boto3 azure-storage-blob azure-identity --break-system-packages --no-cache-dir
COPY omnibioai-tool-runtime/tools /app/tools
COPY omnibioai-tool-runtime/omni_tool_runtime /app/omni_tool_runtime
COPY omnibioai-tool-runtime/pyproject.toml /app/pyproject.toml
WORKDIR /app
RUN pip3 install -e . --break-system-packages
CMD ["python3", "-m", "tools.generic_sif_runner.run"]
