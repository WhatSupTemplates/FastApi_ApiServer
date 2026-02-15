"""
샘플 할일 API 엔드포인트 (인증 필요 사용자 전용 리소스 예제)
"""
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.sample_task import SampleTaskService
from app.schemas.sample_task import SampleTaskCreate, SampleTaskUpdate, SampleTaskResponse
from app.repositories.sample_task import SampleTaskRepository
from app.models.user import User
from app.api.deps import get_current_active_user  # 인증 의존성
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============================================================
# 의존성 주입 헬퍼
# ============================================================
def get_sample_task_repo(db: AsyncSession = Depends(get_db)) -> SampleTaskRepository:
    """SampleTaskRepository 의존성"""
    return SampleTaskRepository(db)


def get_sample_task_service(repo: SampleTaskRepository = Depends(get_sample_task_repo)) -> SampleTaskService:
    """SampleTaskService 의존성"""
    return SampleTaskService(repo)


# ============================================================
# 보호된 엔드포인트 (인증 필요)
# ============================================================
@router.get("/", response_model=List[SampleTaskResponse])
async def list_my_sample_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> Any:
    """
    내 샘플 할일 목록 조회
    보호된 엔드포인트 - 인증 필요 (자신의 할일만 조회 가능)
    """
    tasks = await service.get_user_tasks(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return tasks


@router.get("/completed", response_model=List[SampleTaskResponse])
async def list_completed_sample_tasks(
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> Any:
    """
    내 완료된 샘플 할일 목록 조회
    보호된 엔드포인트 - 인증 필요
    """
    tasks = await service.get_completed_tasks(user_id=current_user.id)
    return tasks


@router.get("/{task_id}", response_model=SampleTaskResponse)
async def get_sample_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> Any:
    """
    특정 샘플 할일 조회
    보호된 엔드포인트 - 인증 필요 (자신의 할일만 조회 가능)
    """
    task = await service.get_task_by_id(task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일을 찾을 수 없거나 접근 권한이 없습니다"
        )
    return task


@router.post("/", response_model=SampleTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_sample_task(
    task_data: SampleTaskCreate,
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> Any:
    """
    샘플 할일 생성
    보호된 엔드포인트 - 인증 필요 (로그인한 사용자의 할일로 생성)
    """
    new_task = await service.create_task(
        user_id=current_user.id,  # 현재 사용자 ID 자동 할당
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
    )
    return new_task


@router.patch("/{task_id}", response_model=SampleTaskResponse)
async def update_sample_task(
    task_id: int,
    task_data: SampleTaskUpdate,
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> Any:
    """
    샘플 할일 수정
    보호된 엔드포인트 - 인증 필요 (자신의 할일만 수정 가능)
    """
    updated_task = await service.update_task(
        task_id=task_id,
        user_id=current_user.id,  # 권한 확인용
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일을 찾을 수 없거나 접근 권한이 없습니다"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),  # 인증 필요
    service: SampleTaskService = Depends(get_sample_task_service),
) -> None:
    """
    샘플 할일 삭제
    보호된 엔드포인트 - 인증 필요 (자신의 할일만 삭제 가능)
    """
    deleted = await service.delete_task(task_id=task_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할일을 찾을 수 없거나 접근 권한이 없습니다"
        )
