FROM debian:bookworm-slim

# Instalare dependențe
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    procps \
    iproute2 \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Copiere script
COPY ./scripts/monitoring.sh /usr/local/bin/monitoring.sh
RUN chmod +x /usr/local/bin/monitoring.sh

# Setări implicite
ENV INTERVAL=5
ENV DATA_DIR=/data
ENV LOG_FILE=$DATA_DIR/system-state.log

# Creare volum și asigurare permisiuni
RUN mkdir -p /data && chmod -R 777 /data

# Directorul de lucru din container
WORKDIR /data
VOLUME ["/data"]

# Comandă implicită
CMD ["/usr/local/bin/monitoring.sh"]