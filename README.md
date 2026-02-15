# FastAPI Backend Template

FastAPI 기반 프로덕션 레디 백엔드 템플릿 - Enum 기반 공통 코드 관리, JWT 인증, 레이어드 아키텍처

---

## 🎯 프로젝트 개요

- **목적**: 프로덕션 환경에서 바로 사용 가능한 FastAPI 백엔드 템플릿
- **프레임워크**: FastAPI (비동기 지원)
- **아키텍처**: Service-Repository Pattern (레이어드 아키텍처)
- **데이터베이스**: SQLite (개발) / PostgreSQL (프로덕션 대응)
- **인증**: JWT (Access + Refresh Token) + Argon2 비밀번호 해싱
- **특징**: Enum 기반 공통 코드 관리 시스템

### 🌟 주요 기능

- ✅ **이메일 기반 인증** - 로그인, 회원가입, 토큰 갱신
- ✅ **JWT 토큰** - Access Token (30분) + Refresh Token (7일)
- ✅ **공통 코드 관리** - Python Enum → DB 자동 동기화
- ✅ **샘플 리소스** - 인증 필요/불필요 API 예제
- ✅ **프론트엔드 샘플** - 인증 플로우 테스트 페이지
- ✅ **CORS 설정** - 프론트엔드 통합 준비 완료
- ✅ **Swagger UI** - 자동 API 문서화

---

## 📁 프로젝트 구조

```
FastApi_ApiServer/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # 인증 엔드포인트 (로그인, 토큰 갱신)
│   │   │   ├── users.py         # 사용자 관리 (회원가입, 프로필)
│   │   │   ├── sample_posts.py  # 공개 리소스 샘플 (인증 불필요)
│   │   │   └── sample_tasks.py  # 인증 리소스 샘플 (로그인 필요)
│   │   └── deps.py              # 의존성 주입 (인증, Repository)
│   ├── core/
│   │   ├── config.py            # 환경 변수 설정
│   │   ├── database.py          # DB 연결 + 공통 코드 동기화
│   │   ├── security.py          # JWT, 암호화, 해싱
│   │   └── codes.py             # 공통 코드 Enum 정의
│   ├── models/                  # SQLAlchemy ORM 모델
│   │   ├── user.py
│   │   ├── common_code.py       # 공통 코드 DB 모델
│   │   ├── sample_post.py
│   │   └── sample_task.py
│   ├── repositories/            # 데이터 접근 계층
│   │   ├── __init__.py          # BaseRepository
│   │   └── user.py
│   ├── services/                # 비즈니스 로직 계층
│   │   └── user.py
│   ├── schemas/                 # Pydantic 스키마 (검증)
│   │   ├── auth.py
│   │   └── user.py
│   └── main.py                  # FastAPI 애플리케이션
├── samples/
│   └── front_sample.html        # 프론트엔드 인증 샘플
├── .env.example                 # 환경 변수 템플릿
├── environment.yml              # Conda 환경 설정
└── README.md
```

### 아키텍처 계층 구조

```
┌─────────────────────────────────────────┐
│  API Layer (Endpoints)                  │  ← HTTP 요청/응답 처리
├─────────────────────────────────────────┤
│  Service Layer (Business Logic)         │  ← 비즈니스 로직, 검증
├─────────────────────────────────────────┤
│  Repository Layer (Data Access)         │  ← DB 쿼리 추상화
├─────────────────────────────────────────┤
│  Model Layer (ORM Entities)             │  ← SQLAlchemy 모델
└─────────────────────────────────────────┘
```

---

## 🛠️ 기술 스택

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **Framework** | FastAPI | ASGI 웹 프레임워크 |
| **Server** | Uvicorn | ASGI 서버 |
| **ORM** | SQLAlchemy 2.0 | 비동기 ORM |
| **Validation** | Pydantic v2 | 데이터 검증 |
| **Auth** | python-jose | JWT 토큰 |
| **Password** | Argon2 | 비밀번호 해싱 |
| **Encryption** | cryptography | AES-256 암호화 |
| **Database** | SQLite / PostgreSQL | 개발 / 프로덕션 |

---

## 📦 설치 및 실행

### 1. 환경 설정

```bash
# Conda 환경 생성
conda env create -f environment.yml

# 환경 활성화
conda activate fastapi-ai-server
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성 (서버 최초 실행 시 자동 생성되지만 수동 생성도 가능)
cp .env.example .env
```

`.env` 파일 예시:
```env
# Database
DB_TYPE=sqlite
SQLITE_DB_PATH=./data/app.db

# Security (프로덕션에서는 반드시 변경!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
AES_SECRET_KEY=your-super-secret-aes-key-change-this-in-production

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### 3. 서버 실행

```bash
# 개발 서버 (핫 리로드)
python -m uvicorn app.main:app --reload

# 프로덕션
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

서버가 시작되면:
- API 문서: http://127.0.0.1:8000/docs
- 프론트엔드 샘플: http://127.0.0.1:8000/samples/front_sample.html

---

## 🔐 인증 시스템

### JWT Token Flow

1. **로그인** → Access Token (30분) + Refresh Token (7일) 발급
2. **API 호출** → Access Token으로 인증
3. **토큰 만료** → Refresh Token으로 갱신
4. **자동 갱신** → 클라이언트에서 401 에러 시 자동 갱신 후 재시도

### API 엔드포인트

#### 인증 (Authentication)
```http
POST /api/v1/auth/login          # 로그인 (이메일 + 비밀번호)
POST /api/v1/auth/refresh        # 토큰 갱신 (Refresh Token)
```

#### 사용자 (Users)
```http
POST /api/v1/users/register      # 회원가입 (공개)
GET  /api/v1/users/me            # 내 프로필 조회 (인증 필요)
```

#### 샘플 리소스
```http
# 공개 API (인증 불필요)
GET  /api/v1/sample-posts        # 게시물 목록
POST /api/v1/sample-posts        # 게시물 생성

# 인증 API (로그인 필요)
GET  /api/v1/sample-tasks        # 내 할일 목록
POST /api/v1/sample-tasks        # 할일 생성
```

---

## 🎨 공통 코드 관리 시스템

### 특징
- **Python Enum 기반** - 타입 안전, IDE 자동완성 지원
- **DB 자동 동기화** - 서버 시작 시 `codes.py` → DB 자동 반영
- **CRUD 자동화** - 코드 추가/수정/삭제 자동 처리

### 사용 방법

#### 1. `app/core/codes.py`에서 Enum 정의
```python
class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

CODE_METADATA = {
    CodeGroup.USER_STATUS: {
        "group_name": "사용자 상태",
        "description": "사용자 계정의 활성화 상태",
        "codes": {
            UserStatus.ACTIVE: {"name": "활성", "order": 1},
            UserStatus.INACTIVE: {"name": "비활성", "order": 2},
            UserStatus.SUSPENDED: {"name": "정지", "order": 3},
        }
    }
}
```

#### 2. Python 코드에서 직접 사용
```python
from app.core.codes import UserStatus

# 타입 안전한 코드 사용
if user.status == UserStatus.ACTIVE:
    # IDE가 자동완성 지원!
    pass
```

#### 3. 서버 재시작 → 자동 DB 동기화
```
✅ 공통 코드 동기화 완료: 3개 그룹, 총 코드 수 확인됨
```

### DB 구조
```
common_codes 테이블:
├─ group_code="CODE_GROUP", code="USER_STATUS", name="사용자 상태"  (그룹)
├─ group_code="USER_STATUS", code="ACTIVE", name="활성"            (코드)
└─ group_code="USER_STATUS", code="INACTIVE", name="비활성"         (코드)
```

---

## 🖥️ 프론트엔드 샘플 사용법

### 접속
```
http://127.0.0.1:8000/samples/front_sample.html
```

### 테스트 시나리오

1. **회원가입**
   - 이메일: `test@example.com`
   - 사용자명: `testuser` (Display Name)
   - 비밀번호: `Password123` (대문자+소문자+숫자)

2. **로그인**
   - 이메일로 로그인
   - Access Token + Refresh Token 발급됨

3. **인증 API 호출**
   - "인증 API" 버튼 → 내 프로필 조회

4. **자동 갱신 테스트**
   - "자동 갱신 테스트" 버튼
   - 토큰 만료 시 자동으로 Refresh Token으로 갱신 후 재시도

---

## 📚 API 문서

서버 실행 후 Swagger UI 접속:
```
http://127.0.0.1:8000/docs
```

**주요 기능:**
- 모든 API 엔드포인트 문서화
- 직접 테스트 가능 (Try it out)
- 스키마 자동 생성
- JWT 인증 지원 (🔒 Authorize 버튼)

---

## � 개발 가이드

### 새 리소스 추가 방법

#### 1. Model 생성 (`app/models/your_model.py`)
```python
class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

#### 2. Schema 정의 (`app/schemas/your_schema.py`)
```python
class YourCreate(BaseModel):
    name: str

class YourResponse(BaseModel):
    id: int
    name: str
```

#### 3. Repository 생성 (`app/repositories/your_repo.py`)
```python
class YourRepository(BaseRepository[YourModel]):
    async def get_by_name(self, name: str):
        # 커스텀 쿼리
        pass
```

#### 4. Service 생성 (`app/services/your_service.py`)
```python
class YourService:
    def __init__(self, repo: YourRepository):
        self.repo = repo
    
    async def create(self, data):
        # 비즈니스 로직
        pass
```

#### 5. API 엔드포인트 (`app/api/v1/your_api.py`)
```python
@router.post("/")
async def create_item(
    data: YourCreate,
    service: YourService = Depends(get_your_service)
):
    return await service.create(data)
```

#### 6. 라우터 등록 (`app/main.py`)
```python
from app.api.v1 import your_api
app.include_router(your_api.router, prefix="/api/v1/your-resource", tags=["Your Resource"])
```

---

## 🚀 프로덕션 배포

### 환경 변수 확인
```bash
# .env 파일에서 다음 항목 반드시 변경:
JWT_SECRET_KEY=<강력한-랜덤-키>
AES_SECRET_KEY=<강력한-랜덤-키>
DB_TYPE=postgresql
DB_HOST=<your-db-host>
BACKEND_CORS_ORIGINS=["https://your-domain.com"]
```

### PostgreSQL 사용
```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
```

### Docker (선택사항)
```bash
# TODO: Dockerfile 작성 예정
```

---

## 📝 참고사항

### 비밀번호 정책
- 최소 8자 이상
- 대문자 1개 이상
- 소문자 1개 이상
- 숫자 1개 이상

### 토큰 만료 시간
- Access Token: 30분 (기본값, 변경 가능)
- Refresh Token: 7일 (기본값, 변경 가능)

### CORS 설정
기본적으로 모든 origin 허용 (`allow_origins=["*"]`)
프로덕션에서는 `.env`의 `BACKEND_CORS_ORIGINS`로 제한

---

## 🤝 기여

이슈 및 PR 환영합니다!

## 📄 라이선스

MIT License