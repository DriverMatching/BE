# 1. Python 3.10을 기반으로 이미지를 설정
FROM python:3.10

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 앱 코드와 모델 파일들 복사
COPY ./BE /app 

# 4. 의존성 파일 복사
COPY requirements.txt /app/requirements.txt

# 5. 의존성 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# 6. FastAPI 앱 실행에 필요한 포트 열기
EXPOSE 80

# 7. FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
