from fastapi import APIRouter, HTTPException
import googlemaps
import pickle
import logging
from models.driver_recommendation import DriverMatching 

router = APIRouter()

GOOGLE_MAPS_API_KEY = "AIzaSyAUNrCgGKTQuvgmUPMcCmZEjT18IMwEpBw"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# 피클 파일 로드 함수
def load_model():
    try:
        with open("models/driver_matching_model.pkl", "rb") as file:
            model = pickle.load(file)
            
        # 🚀 모델이 `DriverMatching` 인스턴스인지 확인
        if not isinstance(model, DriverMatching):
            raise ValueError("🚨 로드된 모델이 `DriverMatching` 인스턴스가 아닙니다.")

        # 🚀 `best_driver()` 메서드 존재 여부 확인
        if not hasattr(model, "best_driver"):
            raise AttributeError("🚨 `best_driver()` 메서드가 존재하지 않습니다.")

        print("✅ 피클 파일 로드 성공")
        
        return model
    except Exception as e:
        logging.error(f"피클 파일 로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"피클 파일 로드 실패: {str(e)}")

# 피클 파일 로드
model = load_model()
print(f"✅ 로드된 모델 타입: {type(model)}")  # 🚀 모델 타입 출력

# 주소 → 위도/경도 변환 함수
def get_lat_lng(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            raise HTTPException(status_code=400, detail="위도/경도 변환 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Maps API 오류: {str(e)}")

# 기사 매칭 API
@router.post("/match-driver")
async def match_driver(data: dict):
    try:
        logging.info(f"사용자 입력 데이터: {data}")  # 입력값

        # 출발지/도착지 주소를 위/경도로 변환
        start_lat, start_lng = get_lat_lng(data["start_address"])
        end_lat, end_lng = get_lat_lng(data["end_address"])

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

        logging.info(f"변환된 사용자 입력값: {user_input}")

        # 기사 추천 실행
        best_driver = model.best_driver(user_input)

        # 결과 반환
        if best_driver is None:
            return {"message": "적합한 기사를 찾을 수 없습니다."}
        
        return best_driver.to_dict()
    
    except Exception as e:
        logging.error(f"🚨 기사 추천 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"🚨 기사 추천 실패: {str(e)}")