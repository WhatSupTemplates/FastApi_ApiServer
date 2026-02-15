"""
샘플 게시물 서비스 (인증 불필요 공개 리소스 예제)
"""
from typing import Optional, List
from app.repositories.sample_post import SamplePostRepository
from app.models.sample_post import SamplePost


class SamplePostService:
    """
    샘플 게시물 관련 비즈니스 로직을 처리하는 서비스
    공개 리소스이므로 특별한 권한 확인 불필요
    """
    
    def __init__(self, post_repo: SamplePostRepository):
        self.post_repo = post_repo
    
    async def get_by_id(self, post_id: int) -> Optional[SamplePost]:
        """ID로 게시물 조회"""
        return await self.post_repo.get_by_id(post_id)
    
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[SamplePost]:
        """모든 게시물 조회 (최신순)"""
        return await self.post_repo.get_recent_posts(skip, limit)
    
    async def create_post(
        self, 
        title: str, 
        content: str, 
        author_name: str
    ) -> SamplePost:
        """
        신규 게시물 생성
        인증 불필요 - 누구나 게시물 작성 가능
        """
        post_data = {
            "title": title,
            "content": content,
            "author_name": author_name,
        }
        return await self.post_repo.create(post_data)
    
    async def update_post(
        self, 
        post_id: int, 
        title: Optional[str] = None,
        content: Optional[str] = None,
        author_name: Optional[str] = None,
    ) -> Optional[SamplePost]:
        """게시물 수정"""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if author_name is not None:
            update_data["author_name"] = author_name
        
        if not update_data:
            return await self.post_repo.get_by_id(post_id)
        
        return await self.post_repo.update(post_id, update_data)
    
    async def delete_post(self, post_id: int) -> bool:
        """게시물 삭제"""
        return await self.post_repo.delete(post_id)
