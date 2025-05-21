import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.batch.location.recommendation.train_lightfm import train_and_save_model

def run():
    print(">>> LightFM 추천 모델 학습 시작")
    train_and_save_model()
    print(">>> 학습 완료 및 모델 저장 성공")
