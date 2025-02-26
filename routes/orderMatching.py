from fastapi import APIRouter, HTTPException
import googlemaps
import pickle
import logging
from models.driver_recommendation import DriverMatching, get_train_data

router = APIRouter()

GOOGLE_MAPS_API_KEY = "AIzaSyAUNrCgGKTQuvgmUPMcCmZEjT18IMwEpBw"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# train_data를 가져오기
train_data = get_train_data()

# 피클 파일 로드 함수
def load_model():
    try:
        with open("models/driver_matching_model.pkl", "rb") as file:
            model = pickle.load(file)
        
        # 피클 파일에서 불러온 모델에 train_data 설정
        model.df = train_data
        
        print("피클 파일 로드 성공")
        return model
    
    except Exception as e:
        logging.error(f"피클 파일 로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"피클 파일 로드 실패: {str(e)}")

# 피클 파일 로드
model = load_model()

# 기사 매칭 API
@router.post("/match-driver")
async def match_driver(data: dict):
    try:
        # 출발지/도착지 주소를 위/경도로 변환
        start_lat, start_lng = gmaps.geocode(data["start_address"])[0]["geometry"]["location"].values()
        end_lat, end_lng = gmaps.geocode(data["end_address"])[0]["geometry"]["location"].values()

        # 변환된 위경도 및 추가 정보 저장
        user_input = {
            "origin_latitude": start_lat,
            "origin_longitude": start_lng,
            "destination_latitude": end_lat,
            "destination_longitude": end_lng,
            "cold_storage": data["cold_storage"],
            "hazardous_material": data["hazardous_material"],
            "fragile_item": data["fragile_item"],
            "item_weight": int(float(data["weight"])),
            "quantity": int(float(data["quantity"]))
        }

        print(f"변환된 사용자의 입력값: {user_input}")

        # 기사 추천 실행
        best_driver = model.best_driver(user_input)

        # 결과 반환
        if best_driver is None:
            return {"message": "적합한 기사를 찾을 수 없습니다."}

        return {"matchedDriver": best_driver}  # 프론트에서 navigate()에 사용할 state 포함

    except Exception as e:
        logging.error(f"기사 추천 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"기사 추천 실패: {str(e)}")