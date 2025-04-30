import pytest
from uuid import uuid4
from app.services.recommendation_service import RecommendationService
from app.db.models.location import Location


def create_location(id=None, category_name=None, x=127.192889, y=37.563083):
    """
    기본 위치는 미사역 기준
    """
    return Location(
        id=id or uuid4(),
        kakao_place_id="kakao_id_" + (str(id) if id else ""),
        name="test",
        category_group_code="CG",
        category_group_name="CGN",
        category_name=category_name,
        phone=None,
        address_name="경기도 하남시",
        road_address_name="경기도 하남시",
        x=x,
        y=y,
        place_url=None,
        use_yn='Y',
        delete_yn='N'
    )

@pytest.mark.parametrize("tags, expected_order", [
    (['카페'],   ['loc_cafe', 'loc_both', 'loc_none']),
    (['공원'],  ['loc_park', 'loc_both', 'loc_none']),
])
def test_recommend_mvp_ordering(db_session, tags, expected_order):
    # 거리 영향 없이 태그 기반 순서만 검증
    loc_none = create_location(id=uuid4(), category_name='음식 > 기타')
    loc_cafe = create_location(id=uuid4(), category_name='카페 > 디저트')
    loc_park = create_location(id=uuid4(), category_name='공원')
    loc_both = create_location(id=uuid4(), category_name='카페 > 공원')
    for loc in [loc_none, loc_cafe, loc_park, loc_both]:
        db_session.add(loc)
    db_session.commit()

    schedule = RecommendationService.recommend_mvp(
        tags=tags,
        days=1,
        per_day_count=3,
        db=db_session
    )
    cats = [loc.category_name for loc in schedule[0]]
    mapping = {
        'loc_none': '음식 > 기타',
        'loc_cafe': '카페 > 디저트',
        'loc_park': '공원',
        'loc_both': '카페 > 공원',
    }
    expected = [mapping[n] for n in expected_order]
    assert cats == expected


def test_recommend_mvp_distance_effect(db_session):
    # 동일 태그, 거리 차이에 따른 순서 검증
    tag = ['박물관']
    loc_near = create_location(
        id=uuid4(), category_name='박물관', x=127.192889, y=37.563083
    )
    loc_far = create_location(
        id=uuid4(), category_name='박물관', x=126.970656, y=37.554644
    )
    db_session.add_all([loc_near, loc_far])
    db_session.commit()

    schedule = RecommendationService.recommend_mvp(
        tags=tag,
        days=1,
        per_day_count=2,
        db=db_session
    )
    result = schedule[0]
    assert result[0].id == loc_near.id
    assert result[1].id == loc_far.id


def test_recommend_mvp_weighted_sum(db_session):
    # 콘텐츠와 거리 점수를 모두 고려해 복합 순서 검증
    tags = ['카페']
    # 높은 콘텐츠, 먼 거리 => 가장 높은 점수
    loc_high_content_far = create_location(
        id=uuid4(), category_name='카페', x=126.970656, y=37.554644
    )
    # 높은 콘텐츠, 가까운 거리 => 두 번째 점수
    loc_best = create_location(
        id=uuid4(), category_name='카페 > 공원', x=127.192889, y=37.563083
    )
    # 중간 콘텐츠, 중간 거리 => 세 번째 점수
    loc_mid = create_location(
        id=uuid4(), category_name='카페 > 디저트', x=127.081772, y=37.560000
    )
    # 낮은 콘텐츠, 가까운 거리 => 네 번째 점수
    loc_low_content_near = create_location(
        id=uuid4(), category_name='음식 > 기타', x=127.192889, y=37.563083
    )
    db_session.add_all([loc_high_content_far, loc_best, loc_mid, loc_low_content_near])
    db_session.commit()

    schedule = RecommendationService.recommend_mvp(
        tags=tags,
        days=1,
        per_day_count=4,
        db=db_session
    )
    result_ids = [loc.id for loc in schedule[0]]

    # 기대 순서: loc_high_content_far, loc_best, loc_mid, loc_low_content_near
    assert result_ids == [
        loc_high_content_far.id,
        loc_best.id,
        loc_mid.id,
        loc_low_content_near.id
    ]
