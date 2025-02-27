# Pydantic 데이터 모델 정의
from pydantic import BaseModel
from typing import Dict, Any

class MatchingData(BaseModel):
    customer: Dict[str, Any]
    driver: Dict[str, Any]
