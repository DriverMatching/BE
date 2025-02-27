import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models.MatchingHistory import MatchingHistory
from crud import save_matching, update_review
from schemas import MatchingData
from routes.orderMatching import router as order_matching_router

# 로깅 설정 추가
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# CORS 설정 추가 (React 프론트엔드에서 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테이블 자동 생성
print("데이터베이스 테이블 생성 시작")
Base.metadata.create_all(bind=engine)
print("테이블 생성 완료")

# 라우터 등록
app.include_router(order_matching_router)

@app.post("/match-driver")
async def match_driver(data: dict):
    return {"message": "기사 매칭 성공"}

# 매칭 정보 저장 API
@app.post("/save-matching")
def save_matching_api(data: MatchingData, db: Session = Depends(get_db)):
    try:
        saved_match = save_matching(db, data.customer, data.driver) 
        return {"message": "매칭 정보가 성공적으로 저장되었습니다!", "match_id": saved_match.id}
    
    except Exception as e:
        logging.error(f"매칭 저장 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="매칭 저장 실패")

# 고객이 배송 상태, 친절도, 별점을 평가하는 API
@app.put("/update-review/{match_id}")
def update_review_api(match_id: int, review_data: dict, db: Session = Depends(get_db)):
    updated_match = update_review(db, match_id, review_data)
    
    if updated_match is None:
        raise HTTPException(status_code=404, detail="매칭 기록을 찾을 수 없습니다.")

    return {"message": "평가가 저장되었습니다!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
