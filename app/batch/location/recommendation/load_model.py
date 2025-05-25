import os
import pickle
from lightfm import LightFM
from datetime import datetime
from scipy.sparse import csr_matrix


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

def load_trained_model(date_str: str = None) -> tuple[LightFM, dict, dict, csr_matrix]:
    """
    LightFM 모델과 인덱스 정보 로드
    date_str: '20250524' 같은 날짜 문자열 (기본은 오늘 날짜)
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    path = os.path.join(MODEL_DIR, f"lightfm_model_{date_str}.pkl")
    # path = os.path.join(MODEL_DIR, f"lightfm_model.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"모델 파일이 존재하지 않습니다: {path}")

    with open(path, "rb") as f:
        data = pickle.load(f)
        return data["model"], data["user_idx"], data["item_idx"], data["item_features"]


def load_user_interactions(date_str: str = None) -> tuple[dict, dict, dict]:
    """
    모델 학습 당시 저장된 유저-아이템 인덱스 정보만 불러옴
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    path = os.path.join(MODEL_DIR, f"lightfm_model_{date_str}.pkl")
    # path = os.path.join(MODEL_DIR, f"lightfm_model.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"모델 파일이 존재하지 않습니다: {path}")

    with open(path, "rb") as f:
        data = pickle.load(f)
        return data["user_idx"], data["item_idx"], {v: k for k, v in data["item_idx"].items()}