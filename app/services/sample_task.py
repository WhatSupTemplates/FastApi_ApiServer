"""
샘플 할일 서비스 (인증 필요 사용자 전용 리소스 예제)
"""
from typing import Optional, List
from app.repositories.sample_task import SampleTaskRepository
from app.models.sample_task import SampleTask


class SampleTaskService:
    """
    샘플 할일 관련 비즈니스 로직을 처리하는 서비스
    사용자별 데이터 격리가 중요 - 반드시 user_id 확인 필요
    """
    
    def __init__(self, task_repo: SampleTaskRepository):
        self.task_repo = task_repo
    
    async def get_user_tasks(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SampleTask]:
        """특정 사용자의 모든 할일 조회"""
        return await self.task_repo.get_by_user(user_id, skip, limit)
    
    async def get_completed_tasks(self, user_id: int) -> List[SampleTask]:
        """특정 사용자의 완료된 할일 조회"""
        return await self.task_repo.get_completed_by_user(user_id)
    
    async def get_task_by_id(self, task_id: int, user_id: int) -> Optional[SampleTask]:
        """
        특정 할일 조회 (권한 확인 포함)
        다른 사용자의 할일은 접근 불가
        """
        return await self.task_repo.get_by_id_and_user(task_id, user_id)
    
    async def create_task(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        is_completed: bool = False,
    ) -> SampleTask:
        """
        신규 할일 생성
        인증 필요 - 현재 로그인한 사용자의 할일로 생성
        """
        task_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "is_completed": is_completed,
        }
        return await self.task_repo.create(task_data)
    
    async def update_task(
        self,
        task_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> Optional[SampleTask]:
        """
        할일 수정 (권한 확인 포함)
        자신의 할일만 수정 가능
        """
        # 권한 확인: 해당 할일이 현재 사용자의 것인지 확인
        existing_task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not existing_task:
            return None
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if is_completed is not None:
            update_data["is_completed"] = is_completed
        
        if not update_data:
            return existing_task
        
        return await self.task_repo.update(task_id, update_data)
    
    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        할일 삭제 (권한 확인 포함)
        자신의 할일만 삭제 가능
        """
        # 권한 확인: 해당 할일이 현재 사용자의 것인지 확인
        existing_task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not existing_task:
            return False
        
        return await self.task_repo.delete(task_id)
