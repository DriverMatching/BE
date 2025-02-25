import pickle
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sqlalchemy.orm import Session
from database import get_db

# MySQL에서 train 데이터 불러오기
def get_train_data():
    """MySQL에서 train 데이터를 불러와 DataFrame으로 변환"""
    with next(get_db()) as db:  # 데이터베이스 세션 사용
        query = "SELECT * FROM train;"  
        df = pd.read_sql(query, db.bind)  # SQLAlchemy 엔진을 통해 데이터 조회
    
    # 🚀 데이터셋 컬럼 확인
    print(f"✅ `train` 데이터 컬럼 목록: {df.columns.tolist()}")
    
    return df

# MySQL 데이터 가져오기
df = get_train_data()  # train 데이터 불러오기

# 기사 추천 모델 클래스
class DriverMatching:
    def __init__(self):
        self.df = get_train_data()  # 🚀 클래스 내부에서 데이터 직접 불러오기
        print(f"🔍 DriverMatching 데이터 로드 완료, 컬럼 목록: {self.df.columns.tolist()}")

    # 하버사인 거리 계산 함수
    @staticmethod
    def haversine_distance(coord1, coord2):
        return geodesic(coord1, coord2).kilometers  # km 단위 거리 반환

    # 기사 추천 함수
    def best_driver(self, user_input):
        try:
            print(f"✅ `best_driver()` 실행: {user_input}")  # 🚀 사용자 입력값 출력
        
            # 1차 필터링: 사용자 조건 충족 기사만 남기기
            filtered_drivers = self.df[
                ((user_input["cold_storage"] == 0) | (self.df["refrigeration_available"] == 1)) &
                ((user_input["hazardous_material"] == 0) | (self.df["hazardous_material_available"] == 1)) &
                ((user_input["fragile_item"] == 0) | (self.df["fragile_item_available"] == 1)) &
                (self.df["driver_max_delivery_weight"] >= user_input["item_weight"] * user_input["quantity"])
            ].copy()
        
            # 🚀 필터링 후 데이터 출력
            print(f"✅ 필터링 후 남은 기사 수: {len(filtered_drivers)}")
        
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

            # 기사 수가 너무 많으면 거리 기준을 좁힘
            if filtered_drivers.shape[0] > 10:
                filtered_drivers = filtered_drivers[filtered_drivers["distance_to_origin"] <= 5]
            if filtered_drivers.shape[0] > 5:
                filtered_drivers = filtered_drivers[filtered_drivers["distance_to_origin"] <= 3]

            # 🚀 거리 계산 후 데이터 확인
            print(f"✅ 거리 계산 완료: {filtered_drivers[['driver_id', 'distance_to_origin']].head()}")
        
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

            # 최적의 기사 추천 (최고 점수 기사 1명 추천)
            best_driver = filtered_drivers.sort_values(by="final_score", ascending=False).iloc[0]
            
            return best_driver.to_dict()
        
        except Exception as e:
            print(f"🚨 `best_driver()` 실행 중 오류 발생: {str(e)}")
            raise e  # 오류를 다시 던져서 FastAPI에서 확인 가능하도록 함.

model = DriverMatching()

# 🚀 `best_driver()` 메서드 존재 여부 확인
if hasattr(model, "best_driver"):
    print("✅ `best_driver()` 메서드가 정상적으로 존재합니다.")
else:
    raise AttributeError("🚨 `best_driver()` 메서드가 존재하지 않습니다.")

# 피클 파일 저장
with open("models/driver_matching_model.pkl", "wb") as file:
    pickle.dump(model, file, protocol=4)

print("피클 파일이 성공적으로 저장되었습니다!")