"""
샘플 게시물 관련 Pydantic 스키마 (공개 리소스 예제)
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# 기본 스키마
# ============================================================
class SamplePostBase(BaseModel):
    """공통 샘플 게시물 필드를 가진 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="게시물 제목")
    content: str = Field(..., min_length=1, description="게시물 내용")
    author_name: str = Field(..., min_length=1, max_length=100, description="작성자명")


# ============================================================
# 요청 스키마
# ============================================================
class SamplePostCreate(SamplePostBase):
    """샘플 게시물 생성 스키마 (인증 불필요)"""
    pass


class SamplePostUpdate(BaseModel):
    """샘플 게시물 수정 스키마"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    author_name: Optional[str] = Field(None, min_length=1, max_length=100)


# ============================================================
# 응답 스키마
# ============================================================
class SamplePostResponse(SamplePostBase):
    """샘플 게시물 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM 모델로부터 생성 허용
