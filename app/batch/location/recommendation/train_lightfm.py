import os
import pickle
from lightfm import LightFM
from lightfm.evaluation import precision_at_k
from app.batch.location.recommendation.preprocess import preprocess

# 현재 파일 기준 절대 경로로 모델 저장 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "lightfm_model.pkl")

def train_and_save_model():
    # 전처리 함수 실행: 상호작용 행렬, 아이템 특징, 유저/아이템 인덱스 맵 반환
    interactions, item_features, user_idx, item_idx = preprocess()

    # WARP 손실함수를 사용하는 LightFM 모델 생성
    model = LightFM(loss="warp")

    # 모델 학습 (10 epoch, 4개 스레드 사용)
    model.fit(interactions, item_features=item_features, epochs=10, num_threads=4)

    # Precision@5 평가 지표 출력
    score = precision_at_k(model, interactions, item_features=item_features, k=5).mean()
    print(f">>> Precision@5: {score:.4f}")

    # 모델 및 인덱스 정보 저장
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "user_idx": user_idx,
            "item_idx": item_idx
        }, f)

    print(f">>> LightFM 모델 저장 완료: {MODEL_PATH}")