FROM python:3.11-slim

WORKDIR /app

COPY ./scripts/backup.py .

ENV BACKUP_INTERVAL=5
ENV BACKUP_DIR=/data/backup

VOLUME ["/data"]

CMD ["python", "backup.py"]