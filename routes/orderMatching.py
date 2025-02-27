from fastapi import APIRouter, HTTPException, Depends
import googlemaps
import pickle
import logging
from sqlalchemy.orm import Session
from database import get_db
from models.MatchingHistory import MatchingHistory  # 모델 가져오기
from models.driver_recommendation import DriverMatching, get_train_data
from crud import save_matching
from schemas import MatchingData

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

        return {
            "matchedDriver": best_driver,
            "origin_latitude": start_lat,
            "origin_longitude": start_lng,
            "destination_latitude": end_lat,
            "destination_longitude": end_lng
            
        }

    except Exception as e:
        logging.error(f"기사 추천 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"기사 추천 실패: {str(e)}")
    
# 매칭 정보 저장 API (수정됨)
@router.post("/save-matching")
async def save_matching_api(data: MatchingData, db: Session = Depends(get_db)):
    try:
        print("요청된 데이터", data.dict())
        
        saved_match = save_matching(db, data.customer, data.driver)  
        return {"message": "매칭 정보가 성공적으로 저장되었습니다!", "match_id": saved_match.id}

    except Exception as e:
        logging.error(f"매칭 저장 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매칭 저장 실패: {str(e)}")
