FROM python:3.11-slim

WORKDIR /app

COPY ./scripts/backup.py .

ENV BACKUP_INTERVAL=5
ENV DATA_DIR=/data
ENV BACKUP_DIR=/data/backup
ENV LOG_FILE=/data/system-state.log

RUN mkdir -p /data/backup && \
    mkdir -p /data && \
    chmod -R 777 /data

VOLUME [ "/data" ]

CMD ["python", "backup.py"]