"""
샘플 게시물 API 엔드포인트 (인증 불필요 공개 리소스 예제)
"""
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.sample_post import SamplePostService
from app.schemas.sample_post import SamplePostCreate, SamplePostUpdate, SamplePostResponse
from app.repositories.sample_post import SamplePostRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============================================================
# 의존성 주입 헬퍼
# ============================================================
def get_sample_post_repo(db: AsyncSession = Depends(get_db)) -> SamplePostRepository:
    """SamplePostRepository 의존성"""
    return SamplePostRepository(db)


def get_sample_post_service(repo: SamplePostRepository = Depends(get_sample_post_repo)) -> SamplePostService:
    """SamplePostService 의존성"""
    return SamplePostService(repo)


# ============================================================
# 공개 엔드포인트 (인증 불필요)
# ============================================================
@router.get("/", response_model=List[SamplePostResponse])
async def list_sample_posts(
    skip: int = 0,
    limit: int = 10,
    service: SamplePostService = Depends(get_sample_post_service),
) -> Any:
    """
    샘플 게시물 목록 조회
    공개 엔드포인트 - 인증 불필요
    """
    posts = await service.get_all(skip=skip, limit=limit)
    return posts


@router.get("/{post_id}", response_model=SamplePostResponse)
async def get_sample_post(
    post_id: int,
    service: SamplePostService = Depends(get_sample_post_service),
) -> Any:
    """
    특정 샘플 게시물 조회
    공개 엔드포인트 - 인증 불필요
    """
    post = await service.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시물을 찾을 수 없습니다"
        )
    return post


@router.post("/", response_model=SamplePostResponse, status_code=status.HTTP_201_CREATED)
async def create_sample_post(
    post_data: SamplePostCreate,
    service: SamplePostService = Depends(get_sample_post_service),
) -> Any:
    """
    샘플 게시물 생성
    공개 엔드포인트 - 인증 불필요 (누구나 게시물 작성 가능)
    """
    new_post = await service.create_post(
        title=post_data.title,
        content=post_data.content,
        author_name=post_data.author_name,
    )
    return new_post


@router.patch("/{post_id}", response_model=SamplePostResponse)
async def update_sample_post(
    post_id: int,
    post_data: SamplePostUpdate,
    service: SamplePostService = Depends(get_sample_post_service),
) -> Any:
    """
    샘플 게시물 수정
    공개 엔드포인트 - 인증 불필요 (실제 프로덕션에서는 권한 확인 필요)
    """
    updated_post = await service.update_post(
        post_id=post_id,
        title=post_data.title,
        content=post_data.content,
        author_name=post_data.author_name,
    )
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시물을 찾을 수 없습니다"
        )
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample_post(
    post_id: int,
    service: SamplePostService = Depends(get_sample_post_service),
) -> None:
    """
    샘플 게시물 삭제
    공개 엔드포인트 - 인증 불필요 (실제 프로덕션에서는 권한 확인 필요)
    """
    deleted = await service.delete_post(post_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시물을 찾을 수 없습니다"
        )
