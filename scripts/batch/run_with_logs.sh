#!/bin/bash

# 사용법: ./run_with_logs.sh retrain_location_recommendation

JOB_NAME=$1
DATE=$(date '+%Y%m%d')

# 현재 스크립트 파일 기준으로 프로젝트 루트 경로 구하기
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
LOG_DIR="$PROJECT_ROOT/logs"

echo $PROJECT_ROOT

mkdir -p "$LOG_DIR"

ALL_LOG="$LOG_DIR/${JOB_NAME}.log"
DAILY_LOG="$LOG_DIR/${JOB_NAME}_${DATE}.log"

cd "$PROJECT_ROOT" || exit 1

# ENV를 local로 설정
export ENV=local

echo ">>> 실행 시작: $JOB_NAME at $(date)" | tee -a "$ALL_LOG" >> "$DAILY_LOG"
python scripts/batch/batch_runner.py "$JOB_NAME" 2>&1 | tee -a "$ALL_LOG" >> "$DAILY_LOG"
echo ">>> 실행 종료: $JOB_NAME at $(date)" | tee -a "$ALL_LOG" >> "$DAILY_LOG"
echo "" >> "$ALL_LOG"
echo "" >> "$DAILY_LOG"
