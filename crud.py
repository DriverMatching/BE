from sqlalchemy.orm import Session
from models.MatchingHistory import MatchingHistory  

# 기사 매칭 정보를 DB에 저장하는 함수
def save_matching(db: Session, customer_data: dict, driver_data: dict):
    try:
        new_match = MatchingHistory(
            start_address=customer_data["start_address"],
            start_detail=customer_data["start_detail"],
            start_latitude=customer_data["origin_latitude"],
            start_longitude=customer_data["origin_longitude"],
            end_address=customer_data["end_address"],
            end_detail=customer_data["end_detail"],
            end_latitude=customer_data["destination_latitude"],
            end_longitude=customer_data["destination_longitude"],
            item_type_nm=customer_data["item_type_nm"],
            cold_storage=customer_data["cold_storage"],
            fragile_item=customer_data["fragile_item"],
            hazardous_material=customer_data["hazardous_material"],
            weight=customer_data["weight"],
            quantity=customer_data["quantity"],
            driver_id=driver_data["driver_id"],
            distance=driver_data["distance_to_origin"],
            delivery_status=None,
            kindness_rating=None,
            star_rating=None
        )

        db.add(new_match)
        db.commit()
        db.refresh(new_match)

        return new_match
    except Exception as e:
        db.rollback()  # 롤백 추가 (DB 일관성 유지)
        raise e  # 예외 다시 발생

# 기사 평가를 업데이트하는 함수
def update_review(db: Session, match_id: int, review_data: dict):
    match = db.query(MatchingHistory).filter(MatchingHistory.id == match_id).first()
    
    if not match:
        return None

    match.delivery_status = review_data["delivery_status"]
    match.kindness_rating = review_data["kindness_rating"]
    match.star_rating = review_data["star_rating"]

    db.commit()
    db.refresh(match)

    return match
