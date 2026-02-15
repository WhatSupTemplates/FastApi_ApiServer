"""
샘플 게시물 Repository (인증 불필요 공개 리소스 예제)
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sample_post import SamplePost
from app.repositories import BaseRepository


class SamplePostRepository(BaseRepository[SamplePost]):
    """
    샘플 게시물 전용 Repository
    공개 리소스이므로 특별한 권한 확인 불필요
    """

    def __init__(self, session: AsyncSession):
        super().__init__(SamplePost, session)

    async def get_by_title(self, title: str) -> Optional[SamplePost]:
        """제목으로 게시물 조회"""
        result = await self.session.execute(
            select(SamplePost).where(SamplePost.title == title)
        )
        return result.scalar_one_or_none()

    async def get_recent_posts(self, skip: int = 0, limit: int = 10) -> List[SamplePost]:
        """최신 게시물 조회 (생성일 기준 내림차순)"""
        result = await self.session.execute(
            select(SamplePost)
            .order_by(SamplePost.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
