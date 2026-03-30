FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    && wget https://github.com/statgen/METAL/releases/download/2020-05-05/metal.tar.gz \
    && tar -xzf metal.tar.gz \
    && mv metal/metal /usr/local/bin/ \
    && rm -rf metal metal.tar.gz
CMD ["metal"]
