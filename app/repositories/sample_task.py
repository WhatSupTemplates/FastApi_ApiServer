"""
샘플 할일 Repository (인증 필요 사용자 전용 리소스 예제)
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sample_task import SampleTask
from app.repositories import BaseRepository


class SampleTaskRepository(BaseRepository[SampleTask]):
    """
    샘플 할일 전용 Repository
    사용자별로 데이터가 분리되어야 하므로 user_id 필터링 중요
    """

    def __init__(self, session: AsyncSession):
        super().__init__(SampleTask, session)

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SampleTask]:
        """특정 사용자의 모든 할일 조회"""
        result = await self.session.execute(
            select(SampleTask)
            .where(SampleTask.user_id == user_id)
            .order_by(SampleTask.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_completed_by_user(self, user_id: int) -> List[SampleTask]:
        """특정 사용자의 완료된 할일 조회"""
        result = await self.session.execute(
            select(SampleTask)
            .where(SampleTask.user_id == user_id, SampleTask.is_completed == True)
            .order_by(SampleTask.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, task_id: int, user_id: int) -> Optional[SampleTask]:
        """특정 사용자의 특정 할일 조회 (권한 확인용)"""
        result = await self.session.execute(
            select(SampleTask).where(SampleTask.id == task_id, SampleTask.user_id == user_id)
        )
        return result.scalar_one_or_none()
