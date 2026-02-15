"""
사용자 관련 Pydantic 스키마 (요청 및 응답)
"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================
# 기본 스키마
# ============================================================
class UserBase(BaseModel):
    """공통 사용자 필드를 가진 기본 스키마"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, description="사용자명 (3-100자)")


# ============================================================
# 요청 스키마
# ============================================================
class UserCreate(UserBase):
    """사용자 생성(회원가입) 스키마"""
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호 (최소 8자)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        비밀번호 강도 요구사항 검증
        
        요구사항:
        - 대문자 최소 1개
        - 소문자 최소 1개
        - 숫자 최소 1개
        - 최소 8자 이상
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('비밀번호는 최소 1개의 대문자를 포함해야 합니다')
        if not re.search(r'[a-z]', v):
            raise ValueError('비밀번호는 최소 1개의 소문자를 포함해야 합니다')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다')
        return v


class UserUpdate(BaseModel):
    """사용자 정보 수정 스키마"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """사용자 응답 스키마 (비밀번호 제외)"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM 모델로부터 생성 허용


class UserLogin(BaseModel):
    """사용자 로그인 스키마"""
    username: str
    password: str


class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str
