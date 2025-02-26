import pickle
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sqlalchemy.orm import Session
from database import get_db
import logging

# MySQL에서 train 데이터 불러오기
def get_train_data():
    """MySQL에서 train 데이터를 불러와 DataFrame으로 변환"""
    with next(get_db()) as db:  # 데이터베이스 세션 사용
        query = "SELECT * FROM train;"  
        df = pd.read_sql(query, db.bind)  # SQLAlchemy 엔진을 통해 데이터 조회  
    return df

train_data = get_train_data()  

# 기사 추천 모델 클래스
class DriverMatching:
    def __init__(self, train_data):
        self.df = train_data

    # 하버사인 거리 계산 함수
    @staticmethod
    def haversine_distance(coord1, coord2):
        return geodesic(coord1, coord2).kilometers  # km 단위 거리 반환

    # 기사 추천 함수
    def best_driver(self, user_input):
        try:
            # 1차 필터링: 사용자 조건 충족 기사만 남기기
            filtered_drivers = self.df[
                ((user_input["cold_storage"] == 0) | (self.df["refrigeration_available"] == 1)) &
                ((user_input["hazardous_material"] == 0) | (self.df["hazardous_material_available"] == 1)) &
                ((user_input["fragile_item"] == 0) | (self.df["fragile_item_available"] == 1)) &
                (self.df["driver_max_delivery_weight"] >= user_input["item_weight"] * user_input["quantity"])
            ].copy()
        
            # 필터링 후 데이터 출력
            print(f"1차 필터링 후 남은 기사 수: {len(filtered_drivers)}")
        
            # 예외 처리: 조건에 맞는 기사가 없는 경우
            if filtered_drivers.empty:
                print("사용자의 조건에 맞는 기사를 찾을 수 없습니다.")
                return None

            # 출발지 기준 기사와 거리 계산
            filtered_drivers["distance_to_origin"] = filtered_drivers.apply(
                lambda row: self.haversine_distance(
                    (row["driver_latitude"], row["driver_longitude"]),
                    (user_input["origin_latitude"], user_input["origin_longitude"])
                ), axis=1
            )

            # 출발지에서 10km 이내 기사만 남기기
            filtered_drivers = filtered_drivers[filtered_drivers["distance_to_origin"] <= 10]
    
            # 거리 기준으로 필터링 (10km 이내 → 15km → 20km 확장)
            for limit in [10, 15, 20]:
                if len(filtered_drivers) < 10:
                    filtered_drivers = filtered_drivers[filtered_drivers["distance_to_origin"] <= limit]

            # 거리 계산 후 데이터 확인
            print(f"거리 계산 후 남은 기사 수: {len(filtered_drivers)}")
            print(f"거리 계산 완료: {filtered_drivers[['driver_id', 'distance_to_origin']].head()}")

            # 거리 계산 후에도 기사가 없으면 예외 처리
            if filtered_drivers.empty:
                logging.warning("거리 계산 후 매칭 가능한 기사가 없습니다.")
                return None
            
            # 배달 기록이 있는 기사에게 가산점 부여
            filtered_drivers["record_match_score"] = np.random.choice([0, 1], size=len(filtered_drivers), p=[0.7, 0.3])

            # 최종 점수 계산
            filtered_drivers["final_score"] = (
                filtered_drivers["record_match_score"] * 0.25 +  # 배달 경험 가산점 (25%)
                filtered_drivers["years_of_experience"] * 0.3 +  # 경력 (30%)
                filtered_drivers["kindness"] * 0.2 +  # 친절도 (20%)
                filtered_drivers["score"] * 0.15 +  # 별점 (15%)
                filtered_drivers["communication_encoded"] * 0.1  # 의사소통 점수 (10%)
            )

            # 기사 수 확인 후 `.iloc[0]` 호출
            if len(filtered_drivers) == 0:
                logging.warning("점수 계산 후에도 매칭할 기사가 없습니다.")
                return None
            
            # 최적의 기사 추천 (최고 점수 기사 1명 추천)
            best_driver = filtered_drivers.sort_values(by="final_score", ascending=False).iloc[0]
            
            print(f"매칭된 기사 id: {best_driver['driver_id']}, 출발지와의 거리: {round(best_driver['distance_to_origin'], 2)}")

            return {
                "driver_id": int(best_driver["driver_id"]),
                "distance_to_origin": float(best_driver["distance_to_origin"]),
                "years_of_experience": int(best_driver["years_of_experience"]),
                "kindness": float(best_driver["kindness"]),
                "score": float(best_driver["final_score"]),
                "driver_latitude": float(best_driver["driver_latitude"]),
                "driver_longitude": float(best_driver["driver_longitude"]),
                "origin_latitude": float(user_input["origin_latitude"]),
                "origin_longitude": float(user_input["origin_longitude"]),
                "destination_latitude": float(user_input["destination_latitude"]),
                "destination_longitude": float(user_input["destination_longitude"])
            }
        
        except Exception as e:
            logging.error(f"`best_driver()` 실행 중 오류 발생: {str(e)}")
            return None  # FastAPI에서 안전하게 처리할 수 있도록 None 반환

# train_data를 사용하여 `DriverMatching` 객체 생성
model = DriverMatching(train_data)

# 피클 파일 저장
with open("models/driver_matching_model.pkl", "wb") as file:
    pickle.dump(model, file, protocol=4)

logging.info("피클 파일이 성공적으로 저장되었습니다!")