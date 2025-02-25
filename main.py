import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# 라우터 등록
app.include_router(order_matching_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
