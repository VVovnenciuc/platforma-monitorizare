FROM alpine:latest

RUN apk add --no-cache bash coreutils procps iproute2 lm-sensors docker-cli

RUN mkdir -p /data && chmod 777 /data

COPY ./scripts/monitoring.sh /usr/local/bin/monitoring.sh
RUN chmod +x /usr/local/bin/monitoring.sh

ENV INTERVAL=5

VOLUME ["/data"]

WORKDIR /data

CMD ["/usr/local/bin/monitoring.sh"]