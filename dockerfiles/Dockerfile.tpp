FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgomp1 \
    && pip3 install --break-system-packages pyteomics pymzml pandas numpy
# TPP install via conda is recommended for production
CMD ["python3", "-c", "import pyteomics; print('pyteomics ready')"]
