FROM alpine:latest

RUN apk add --no-cache bash coreutils procps

COPY ./scripts/monitoring.sh /usr/local/bin/monitoring.sh
RUN chmod +x /usr/local/bin/monitoring.sh

ENV INTERVAL=5

VOLUME ["/data"]

WORKDIR /data

CMD ["bash", "/usr/local/bin/monitoring.sh"]