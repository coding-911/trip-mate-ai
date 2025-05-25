import os
import pickle
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, recall_at_k, auc_score
from app.batch.location.recommendation.preprocess import preprocess
from datetime import datetime

# 현재 파일 기준 절대 경로로 모델 저장 디렉토리 설정 및 날짜 
today = datetime.now().strftime("%Y%m%d")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", f"lightfm_model_{today}.pkl")

def train_and_save_model():
    # 전처리 함수 실행: 상호작용 행렬, 아이템 특징, 유저/아이템 인덱스 맵 반환
    interactions, item_features, user_idx, item_idx = preprocess()

    # WARP 손실함수를 사용하는 LightFM 모델 생성
    model = LightFM(
        loss="warp",              # 또는 'bpr', 'warp-kos' 등 실험
        no_components=64,         # 기본값 10 → 64로 확장 (더 풍부한 표현)
        learning_rate=0.03,       # 기본 0.05 → 학습 안정성 개선
        random_state=42
    )

    # 모델 학습 (10 epoch, 4개 스레드 사용)
    model.fit(interactions, item_features=item_features, epochs=50, num_threads=4)

    # 평가 지표 출력
    p_at_5 = precision_at_k(model, interactions, item_features=item_features, k=5).mean()
    recall05 = recall_at_k(model, interactions, item_features=item_features, k=5).mean()
    recall10 = recall_at_k(model, interactions, item_features=item_features, k=10).mean()
    recall20 = recall_at_k(model, interactions, item_features=item_features, k=20).mean()
    auc = auc_score(model, interactions, item_features=item_features).mean()

    print(f">>> Precision@5: {p_at_5:.4f}")
    print(f">>> Recall@5: {recall05:.4f}")
    print(f">>> Recall@10: {recall10:.4f}")
    print(f">>> Recall@20: {recall20:.4f}")
    print(f">>> AUC: {auc:.4f}")

    # 모델 및 인덱스 정보 저장
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "user_idx": user_idx,
            "item_idx": item_idx,
            "item_features": item_features, 
        }, f)

    print(f">>> LightFM 모델 저장 완료: {MODEL_PATH}")