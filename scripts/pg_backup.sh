#!/bin/bash

DB_NAME="${POSTGRES_DB}"
DB_USER="${POSTGRES_USER}"
DB_HOST="db"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M)
FILENAME="${DB_NAME}_${DATE}.sql.gz"

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "[+] 백업 시작: ${FILENAME}"
pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" | gzip > "${BACKUP_DIR}/${FILENAME}"
echo "[+] 백업 완료: ${FILENAME}"
