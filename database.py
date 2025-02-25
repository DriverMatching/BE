from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pymysql # MySQL 드라이버 로드

# MySQL 연결 정보 설정 
DATABASE_URL = "mysql+pymysql://admin:k33470115!@database-4.cz02m00ykp2i.ap-northeast-2.rds.amazonaws.com:3306/my_database"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL, echo=True) # echo=True를 설정하면 SQL 쿼리가 로그에 출력 (디버깅용)

# 세션 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 상속해야 함)
Base = declarative_base()

# 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()