from typing import Optional
from app.repositories.user import UserRepository
from app.models.user import User

class UserService:
    """
    사용자 관련 비즈니스 로직을 처리하는 서비스
    """
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return await self.user_repo.get_by_email(email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return await self.user_repo.get_by_username(username)
    
    async def create_user(self, email: str, username: str, password: str) -> User:
        """
        비즈니스 로직 검증과 함께 신규 사용자 생성
        """
        # 비즈니스 로직: 이메일 중복 확인
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("이미 등록된 이메일입니다")
        
        # 비즈니스 로직: 사용자명 중복 확인
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise ValueError("이미 사용중인 사용자명입니다")
        
        # 사용자 생성 (Repository에서 비밀번호 해싱 처리)
        return await self.user_repo.create_user(email, username, password)

    async def authenticate_user(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 인증
        사용자가 존재하고 활성화 상태인 경우 반환, 그렇지 않으면 None 반환
        """
        user = await self.user_repo.get_by_username(username)
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        return user

    async def check_user_exists(self, email: str) -> bool:
        """이메일로 사용자 존재 여부 확인"""
        user = await self.user_repo.get_by_email(email)
        return user is not None
