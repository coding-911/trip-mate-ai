import sys
import os
import importlib

# scripts/batch 하위에서 실행해도 app/ 모듈 import 가능하도록 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(CURRENT_DIR, "batch_jobs")

BATCH_JOBS = {}

# batch_jobs 디렉토리 내의 .py 파일 자동 등록
for filename in os.listdir(JOBS_DIR):
    if filename.endswith(".py") and not filename.startswith("__"):
        job_name = filename[:-3]  # .py 확장자 제거
        module_path = f"scripts.batch.batch_jobs.{job_name}"
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, "run"):
                BATCH_JOBS[job_name] = module.run
        except Exception as e:
            print(f"[ERROR] {module_path} import 실패: {e}")

def run_batch(job_name: str):
    if job_name not in BATCH_JOBS:
        print(f"[ERROR] 등록되지 않은 배치 작업입니다: {job_name}")
        print(f"[INFO] 실행 가능한 배치 목록: {list(BATCH_JOBS.keys())}")
        sys.exit(1)

    print(f">>> 배치 시작: {job_name}")
    try:
        BATCH_JOBS[job_name]()
        print(f">>> 배치 완료: {job_name}")
    except Exception as e:
        print(f"[ERROR] 배치 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] 실행할 배치 이름을 입력하세요.")
        print(f"[USAGE] python {sys.argv[0]} <배치이름>")
        print(f"[INFO] 실행 가능한 배치 목록: {list(BATCH_JOBS.keys())}")
        sys.exit(1)

    batch_name = sys.argv[1]
    run_batch(batch_name)
