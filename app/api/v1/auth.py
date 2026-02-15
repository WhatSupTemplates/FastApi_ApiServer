"""
인증 엔드포인트 (로그인, 회원가입, 토큰 갱신)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.services.user import UserService
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.api.deps import get_user_service

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    """
    사용자 로그인 엔드포인트
    JWT 액세스 토큰과 리프레시 토큰을 반환합니다
    
    참고: OAuth2PasswordRequestForm의 username 필드에 이메일을 입력받습니다
    """
    # 1. 사용자 인증 (이메일로 조회 및 활성화 확인)
    # 참고: OAuth2PasswordRequestForm은 username 필드를 사용하지만, 우리는 이메일을 입력받습니다
    user = await user_service.get_by_email(form_data.username)  # username 필드에 이메일 입력
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 활성화 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다",
        )
    
    # 2. 비밀번호 검증
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 토큰 생성
    access_token = create_access_token(data={"sub": str(user.email)})  # 이메일을 subject로 사용
    refresh_token = create_refresh_token(data={"sub": str(user.email)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    user_service: UserService = Depends(get_user_service),
):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다
    
    Request Body:
    {
        "refresh_token": "eyJ..."
    }
    """
    # 1. 리프레시 토큰 검증
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 토큰에서 사용자 이메일 추출
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 사용자 존재 및 활성화 확인
    user = await user_service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다",
        )
    
    # 4. 새로운 토큰 발급
    new_access_token = create_access_token(data={"sub": str(user.email)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.email)})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
