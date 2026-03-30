FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    zlib1g-dev \
    git \
    && git clone https://github.com/statgen/METAL.git /tmp/metal \
    && cd /tmp/metal && mkdir build && cd build \
    && apt-get install -y cmake \
    && cmake .. && make && make install \
    && ln -s /usr/local/bin/metal /usr/local/bin/metal 2>/dev/null || true
CMD ["metal"]
