#!/bin/bash

BACKUP_DIR="/backup"
LOG_DIR="/logs/pg"
DAYS=30

echo "[*] ${DAYS}일 지난 백업 및 로그 삭제 시작"

# 백업 파일 삭제
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +$DAYS -exec rm -f {} \;

# 일별 로그 삭제
find "$LOG_DIR/backup" -type f -name "backup_*.log" -mtime +$DAYS -exec rm -f {} \;
find "$LOG_DIR/cleanup" -type f -name "cleanup_*.log" -mtime +$DAYS -exec rm -f {} \;

echo "[*] 삭제 완료"
