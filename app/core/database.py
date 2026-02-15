from pathlib import Path
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. 비동기 DB 엔진 생성 (DB로 가는 '고속도로')
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,           # True 설정 시 실행되는 모든 SQL 쿼리가 터미널에 출력됨
    pool_pre_ping=True,   # 사용 전 연결 유효성 확인 (연결 끊김 방지)
)

# 2. 비동기 세션 공장 생성 (데이터를 실어 나를 '트럭' 생산소)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,          # 위에서 만든 고속도로(엔진)를 사용
    class_=AsyncSession,  # 비동기 전용 세션 클래스 사용
    expire_on_commit=False, # 저장(commit) 후에도 객체 데이터를 유지 (비동기 필수)
    autoflush=False,      # 작업 완료 시점까지 DB 반영을 미룸 (제어권 확보)
    autocommit=False,     # 명시적으로 commit 할 때만 실제 DB에 저장됨
)

class Base(DeclarativeBase):
    """
    모든 DB 모델의 부모 클래스.
    이 클래스를 상속받아야 SQLAlchemy가 테이블로 인식함.
    """
    pass


async def get_db():
    """
    API 요청마다 DB 세션을 빌려주는 의존성 함수.
    비동기 컨텍스트 매니저(async with)를 사용해 작업 후 세션을 자동 반납함.
    """
    async with AsyncSessionLocal() as session:
        yield session # 세션을 빌려줌


async def sync_common_codes():
    """
    app/core/codes.py의 Enum 정의를 데이터베이스와 동기화합니다.
    서버 시작 시 자동으로 호출되어 코드 테이블을 최신 상태로 유지합니다.
    
    구조:
    - 그룹: group_code="CODE_GROUP", code="USER_STATUS", name="사용자 상태"
    - 코드: group_code="USER_STATUS", code="ACTIVE", name="활성"
    """
    # 순환 import 방지를 위해 함수 내부에서 import
    from app.core.codes import CODE_METADATA
    from app.models.common_code import CommonCode
    
    CODE_GROUP = "CODE_GROUP"  # 그룹을 나타내는 특수 그룹 코드
    
    async with AsyncSessionLocal() as session:
        synced_groups = 0
        synced_codes = 0
        
        # 1. codes.py의 모든 그룹과 코드 순회
        for group_enum, metadata in CODE_METADATA.items():
            group_code_value = group_enum.value
            
            # 2. 코드 그룹 자체를 레코드로 upsert
            result = await session.execute(
                select(CommonCode).where(
                    CommonCode.group_code == CODE_GROUP,
                    CommonCode.code == group_code_value
                )
            )
            group_record = result.scalar_one_or_none()
            
            if not group_record:
                # 그룹 레코드 생성
                group_record = CommonCode(
                    group_code=CODE_GROUP,
                    code=group_code_value,
                    name=metadata["group_name"],
                    description=metadata.get("description", ""),
                    order=0
                )
                session.add(group_record)
                synced_groups += 1
            else:
                # 그룹 레코드 업데이트
                group_record.name = metadata["group_name"]
                group_record.description = metadata.get("description", "")
            
            # 3. 해당 그룹의 기존 코드 조회
            existing_codes_result = await session.execute(
                select(CommonCode).where(CommonCode.group_code == group_code_value)
            )
            existing_codes = {code.code: code for code in existing_codes_result.scalars().all()}
            
            # 4. codes.py에 정의된 코드 동기화
            defined_code_values = set()
            for code_enum, code_metadata in metadata["codes"].items():
                code_value = code_enum.value
                defined_code_values.add(code_value)
                
                if code_value in existing_codes:
                    # 기존 코드 업데이트
                    existing_code = existing_codes[code_value]
                    existing_code.name = code_metadata["name"]
                    existing_code.order = code_metadata["order"]
                else:
                    # 새 코드 생성
                    new_code = CommonCode(
                        group_code=group_code_value,
                        code=code_value,
                        name=code_metadata["name"],
                        description="",
                        order=code_metadata["order"]
                    )
                    session.add(new_code)
                    synced_codes += 1
            
            # 5. codes.py에 없는 코드는 DB에서 삭제
            codes_to_delete = set(existing_codes.keys()) - defined_code_values
            if codes_to_delete:
                await session.execute(
                    delete(CommonCode).where(
                        CommonCode.group_code == group_code_value,
                        CommonCode.code.in_(codes_to_delete)
                    )
                )
        
        # 6. codes.py에 없는 그룹과 해당 코드들 전체 삭제
        defined_groups = {g.value for g in CODE_METADATA.keys()}
        
        # 6-1. 정의되지 않은 그룹에 속한 코드들 삭제
        await session.execute(
            delete(CommonCode).where(
                CommonCode.group_code.not_in(defined_groups),
                CommonCode.group_code != CODE_GROUP  # "코드그룹"은 제외
            )
        )
        
        # 6-2. 정의되지 않은 그룹 레코드 자체 삭제
        await session.execute(
            delete(CommonCode).where(
                CommonCode.group_code == CODE_GROUP,
                CommonCode.code.not_in(defined_groups)
            )
        )
        
        await session.commit()
        
        # 로그 출력
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"✅ 공통 코드 동기화 완료: {len(CODE_METADATA)}개 그룹, 총 코드 수 확인됨")


async def init_db():
    """
    DB 초기화 함수.
    앱 시작 시 호출되어 작성된 모델(Base 상속)들을 바탕으로 테이블을 생성하고,
    공통 코드를 동기화합니다.
    
    [작동 원리]
    1. 모델 등록: 각 모델 클래스는 `Base`를 상속받을 때 `Base.metadata`라는 중앙 명부에 자동으로 등록됨.
    2. 생성 트리거: `create_all` 명령이 실행될 때 명부에 등록된 모든 테이블 정보를 읽어 DB에 집을 지음.
    3. 중요사항: 파이썬은 파일을 읽어야 내용을 알 수 있으므로, 실행 시점에 모델 파일들이 어딘가에서 
       반드시 `import` 되어야만 테이블이 정상적으로 생성됨 (import가 누락되면 테이블이 안 만들어짐).
    """

    # SQLite인 경우 폴더가 없으면 생성
    if settings.DB_TYPE.lower() == "sqlite":
        db_path = Path(settings.SQLITE_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn: # 트랜잭션 시작
        # 테이블 생성(metadata.create_all)은 동기 방식이므로 run_sync로 실행
        await conn.run_sync(Base.metadata.create_all)
    
    # 공통 코드 동기화
    await sync_common_codes()

