"""
데이터베이스 작업을 위한 Repository 패턴
기본 Repository 클래스 및 예제 구현체
"""
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base
from app.models import User

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    공통 CRUD 작업을 제공하는 기본 Repository
    이 클래스를 상속하여 모델별 Repository를 생성합니다
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """ID로 단일 레코드 조회"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """페이지네이션과 함께 모든 레코드 조회"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        """신규 레코드 생성"""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """기존 레코드 수정"""
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """ID로 레코드 삭제"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0


# UserRepository는 BaseRepository가 정의된 후에 import (순환 참조 방지)
from app.repositories.user import UserRepository  # noqa: E402

__all__ = [
    "BaseRepository",
    "UserRepository",
]

