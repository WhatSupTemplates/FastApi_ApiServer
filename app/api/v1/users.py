"""
사용자 관리 엔드포인트 (회원가입, 프로필 등)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.api.deps import get_current_user, get_user_service
from typing import Any

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    신규 사용자 등록
    인증 불필요한 공개 엔드포인트
    """
    try:
        # 서비스에서 검증 및 생성 처리
        new_user = await user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
        )
        return new_user
    except ValueError as e:
        # 서비스에서 검증 오류 시 ValueError 발생
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    현재 사용자 프로필 조회
    인증 필요한 보호된 엔드포인트
    """
    return current_user
