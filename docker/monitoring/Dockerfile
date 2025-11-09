FROM debian:bookworm-slim

# Instalare dependențe
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    procps \
    iproute2 \
    lm-sensors \
    coreutils \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Instalare Docker CLI (pentru a lista containerele gazdă)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Copiere script
COPY ./scripts/monitoring.sh /usr/local/bin/monitoring.sh
RUN chmod +x /usr/local/bin/monitoring.sh

# Setări implicite
ENV INTERVAL=5
ENV LOG_FILE=/data/system-state.log

# Creare volum și asigurare permisiuni
RUN mkdir -p /data && chmod -R 777 /data

# Directorul de lucru din container
WORKDIR /data

# Comandă implicită
CMD ["/usr/local/bin/monitoring.sh"]