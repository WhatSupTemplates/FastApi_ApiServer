"""
샘플 할일 관련 Pydantic 스키마 (인증 필요 리소스 예제)
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# 기본 스키마
# ============================================================
class SampleTaskBase(BaseModel):
    """공통 샘플 할일 필드를 가진 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="할일 제목")
    description: Optional[str] = Field(None, description="할일 설명")
    is_completed: bool = Field(default=False, description="완료 여부")


# ============================================================
# 요청 스키마
# ============================================================
class SampleTaskCreate(SampleTaskBase):
    """샘플 할일 생성 스키마 (user_id는 자동으로 현재 사용자로 설정)"""
    pass


class SampleTaskUpdate(BaseModel):
    """샘플 할일 수정 스키마"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None


# ============================================================
# 응답 스키마
# ============================================================
class SampleTaskResponse(SampleTaskBase):
    """샘플 할일 응답 스키마"""
    id: int
    user_id: int  # 소유자 ID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM 모델로부터 생성 허용
