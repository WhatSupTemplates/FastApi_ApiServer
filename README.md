# FastAPI AI Server Skeleton

FastAPI 기반 AI 모델 서빙을 위한 백엔드 스켈레톤 프로젝트

---

## 🎯 프로젝트 개요

- **목적**: AI 모델 서빙 및 웹 API 제공
- **프레임워크**: FastAPI
- **아키텍처 패턴**: Service-Repository Pattern (레이어드 아키텍처)
- **데이터베이스**: SQLite (개발) / PostgreSQL (프로덕션)
- **인증**: JWT + Argon2 비밀번호 해싱

### 아키텍처 구조

이 프로젝트는 **Service-Repository Pattern**을 사용하는 레이어드 아키텍처로 구성되어 있습니다:

- **API Layer** (`api/`) - HTTP 엔드포인트, 요청/응답 처리
- **Service Layer** (`services/`) - 비즈니스 로직
- **Repository Layer** (`repositories/`) - 데이터 접근 추상화
- **Model Layer** (`models/`) - ORM 엔티티 (SQLAlchemy)
- **Schema Layer** (`schemas/`) - 데이터 검증 (Pydantic)

이 구조는 관심사의 분리(Separation of Concerns)를 통해 유지보수성과 테스트 용이성을 제공합니다.

---

## 🛠️ 기술 스택

### Backend
| Tech | Version | Description |
| --- | --- | --- |
| FastAPI | 0.104.1 | ASGI 웹 프레임워크 |
| Uvicorn | 0.24.0 | ASGI 서버 |
| SQLAlchemy | 2.0.36 | ORM (Object-Relational Mapping) |
| Argon2 | 20.1.0 | 비밀번호 해싱 |
| Pydantic | 2.6.2 | 데이터 검증 및 모델링 |

### 보안

| Tech | Version | Description |
| --- | --- | --- |
| JWT | 0.1.0 | JSON Web Token |
| Argon2 | 20.1.0 | 비밀번호 해싱 |

---

## 📦 환경 설정

### 필수 요구사항
- **Python**: 3.11+
- **Anaconda** 또는 **Miniconda**

### 설치 방법

#### 1. Conda 환경 생성
```bash
# environment.yml을 사용한 환경 생성
conda env create -f environment.yml

# 환경 활성화
# 환경명은 environment.yml 파일에 있음
conda activate fastapi-ai-server
```

#### 2. 환경 변수 설정
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일 수정 (JWT 시크릿 키 등)
```

#### 3. 데이터베이스 초기화
```bash
# SQLite는 자동 생성됨
# 서버 첫 실행 시 테이블 자동 생성
```

---

## 🚀 실행 방법

### 개발 서버
```bash
# 환경 활성화
conda activate fastapi-ai-server

# 서버 실행 (핫 리로드)
python -m uvicorn app.main:app --reload

# 또는 특정 호스트/포트 지정
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```