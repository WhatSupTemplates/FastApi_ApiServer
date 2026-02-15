from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.core.security import hash_password
from app.repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    사용자 전용 커스텀 메서드를 가진 Repository
    BaseRepository 확장 예제
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, email: str, username: str, password: str) -> User:
        """해싱된 비밀번호와 함께 신규 사용자 생성"""
        hashed_pw = hash_password(password)
        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hashed_pw,
            "is_active": True,
            "is_superuser": False,
        }
        return await self.create(user_data)

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 활성 사용자 조회"""
        result = await self.session.execute(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
