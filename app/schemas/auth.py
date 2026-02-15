"""
인증 관련 Pydantic 스키마 (토큰)
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """디코딩된 토큰 데이터 스키마"""
    user_id: Optional[int] = None
