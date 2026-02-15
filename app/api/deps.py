from typing import Generator, Type, TypeVar, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core import security
from app.models.user import User
from app.repositories import BaseRepository
from app.repositories.user import UserRepository
from app.services.user import UserService

# =================================================================
# [의존성 주입 - 인증]
# =================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    액세스 토큰을 검증하고 현재 사용자를 반환합니다
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 검증할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        if payload is None:
            raise credentials_exception
        email: str = payload.get("sub")  # 토큰에 저장된 이메일을 subject로 사용
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)  # 이메일로 조회
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    현재 사용자가 활성 상태인지 확인합니다
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성 사용자입니다")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    현재 사용자가 관리자인지 확인합니다
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="충분한 권한이 없습니다"
        )
    return current_user


# =================================================================
# [의존성 주입 - Repository]
# 제네릭 Repository 의존성 팩토리
# =================================================================

RepoType = TypeVar("RepoType", bound=BaseRepository)

def get_repository(repo_type: Type[RepoType]) -> Callable[[AsyncSession], RepoType]:
    """
    특정 Repository에 대한 의존성을 생성하는 팩토리 함수
    
    사용법:
        def get_user_repo(repo: UserRepository = Depends(get_repository(UserRepository)))
        
        or direct usage in route:
        @app.get("/users")
        async def read_users(repo: UserRepository = Depends(get_repository(UserRepository))):
    """
    def _get_repo(db: AsyncSession = Depends(get_db)) -> RepoType:
        return repo_type(db)
    return _get_repo

# 일반적인 Repository에 대한 혼헬서 (선택적 짧은 형식)
# get_repository(UserRepository) 대신 get_user_repo를 사용하여 더 깨끗한 코드 작성 가능
get_user_repo = get_repository(UserRepository)


# =================================================================
# [의존성 주입 - Service]
# =================================================================
def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    """UserService 인스턴스를 Repository와 함께 반환합니다"""
    return UserService(user_repo)
