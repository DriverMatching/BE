from fastapi import FastAPI
from routs import driver, matching, order

app = FastAPI()

# API 라우트 등록
app.include_router(driver.router)
app.include_router(matching.router)
app.include_router(order.router)

@app.get("/")
async def home():
    return {"message": "FastAPI 서버가 정상 실행 중입니다!"}