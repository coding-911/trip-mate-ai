import pandas as pd
from elasticsearch import Elasticsearch
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import csr_matrix
from app.db.session import SessionLocal
from app.db.models.location import Location
from app.core.config import settings

def fetch_logs_from_elasticsearch(index: str = "user-events") -> pd.DataFrame:
    print("[1/3] Elasticsearch에서 로그 수집 시작")

    es = Elasticsearch([settings.ELASTICSEARCH_HOSTS])
    resp = es.search(index=index, body={"query": {"match_all": {}}}, size=10000, scroll='2m')
    scroll_id = resp['_scroll_id']
    hits = resp['hits']['hits']
    all_hits = hits.copy()

    while True:
        resp = es.scroll(scroll_id=scroll_id, scroll='2m')
        hits = resp['hits']['hits']
        if not hits:
            break
        all_hits.extend(hits)

    rows = []
    for h in all_hits:
        src = h["_source"]
        rows.append({
            "user_id": src["user_id"],
            "location_id": src["location_id"],
            "action": src["action"],
            "timestamp": src["timestamp"]
        })

    df = pd.DataFrame(rows)
    print(f"총 수집된 로그 수: {len(df)}건")
    return df

def convert_to_interaction_matrix(df: pd.DataFrame) -> tuple[csr_matrix, dict, dict]:
    print("[2/3] 유저-아이템 상호작용 행렬 변환 시작")

    weights = {"view": 1.0, "click": 2.0, "bookmark": 3.0}
    df["score"] = df["action"].map(weights)

    user_idx = {uid: i for i, uid in enumerate(df["user_id"].unique())}
    item_idx = {iid: i for i, iid in enumerate(df["location_id"].unique())}

    rows = df["user_id"].map(user_idx).values
    cols = df["location_id"].map(item_idx).values
    data = df["score"].values

    mat = csr_matrix((data, (rows, cols)), shape=(len(user_idx), len(item_idx)))

    print(f"유저 수: {len(user_idx)}, 아이템 수: {len(item_idx)}")
    print(f"상호작용 행렬 크기: {mat.shape}")
    return mat, user_idx, item_idx

def load_item_features(item_idx: dict) -> csr_matrix:
    print("[3/3] 아이템 특징 행렬 생성 시작")

    db = SessionLocal()
    mlb = MultiLabelBinarizer()

    item_ids = list(item_idx.keys())
    item_id_to_tags = []

    for loc_id in item_ids:
        loc = db.query(Location).filter(Location.id == loc_id).first()
        if loc:
            tags = loc.category_name.split(" > ") if loc.category_name else []
        else:
            tags = []
        item_id_to_tags.append(tags)

    tag_matrix = mlb.fit_transform(item_id_to_tags)
    print(f"태그 원-핫 인코딩 완료, 태그 차원 수: {tag_matrix.shape[1]}")
    return csr_matrix(tag_matrix)

def preprocess():
    print("[START] LightFM 추천 전처리 시작")

    logs_df = fetch_logs_from_elasticsearch()
    interactions, user_idx, item_idx = convert_to_interaction_matrix(logs_df)
    item_features = load_item_features(item_idx)
    print(">>> interactions shape:", interactions.shape)
    print(">>> interactions nnz (non-zero entries):", interactions.nnz)
    print(">>> item_features shape:", item_features.shape)
    print("[DONE] 전처리 완료")

    return interactions, item_features, user_idx, item_idx
