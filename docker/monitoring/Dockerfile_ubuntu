FROM ubuntu:22.04

# Instalare dependențe
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    procps \
    iproute2 \
    lm-sensors \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copiază scriptul
COPY ./scripts/monitoring.sh /usr/local/bin/monitoring.sh
RUN chmod +x /usr/local/bin/monitoring.sh

# Setări
ENV INTERVAL=5
VOLUME ["/data"]
WORKDIR /data

CMD ["/usr/local/bin/monitoring.sh"]