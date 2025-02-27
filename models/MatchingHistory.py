from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, func
from database import Base

# 기사 매칭 기록 테이블 (고객 평가까지 반영)
class MatchingHistory(Base):
    __tablename__ = "usageHistory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 출발지 정보
    start_address = Column(Text, nullable=False)          # 출발지 주소
    start_detail = Column(Text, nullable=True)            # 출발지 상세주소
    start_latitude = Column(Float, nullable=False)        # 출발지 위도
    start_longitude = Column(Float, nullable=False)       # 출발지 경도

    # 도착지 정보
    end_address = Column(Text, nullable=False)            # 도착지 주소
    end_detail = Column(Text, nullable=True)              # 도착지 상세주소
    end_latitude = Column(Float, nullable=False)          # 도착지 위도
    end_longitude = Column(Float, nullable=False)         # 도착지 경도

    # 물품 정보
    item_type_nm = Column(String(100), nullable=False)     # 물품 종류
    cold_storage = Column(Integer, nullable=False)         # 냉장/냉동 여부 (0/1)
    fragile_item = Column(Integer, nullable=False)         # 파손 여부 (0/1)
    hazardous_material = Column(Integer, nullable=False)   # 위험물 여부 (0/1)
    weight = Column(Float, nullable=False)                # 무게 (kg)
    quantity = Column(Integer, nullable=False)            # 수량

    # 기사 정보
    driver_id = Column(Integer, nullable=False)           # 기사 ID
    distance = Column(Float, nullable=False)              # 출발지-기사 거리 (km)

    # 고객이 추가하는 평가 정보
    delivery_status = Column(String(50), nullable=True)  # 배송 상태 
    kindness_rating = Column(Integer, nullable=True)      # 고객이 평가하는 친절도 (1~5)
    star_rating = Column(Integer, nullable=True)         # 별점 (1~5)

    # 생성 시간 (자동 입력)
    created_at = Column(TIMESTAMP, server_default=func.now())
