import logging
import shutil
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.database import init_db, engine, get_db

# ============================================================
# Environment File Setup
# ============================================================
# Create .env from .env.example if it doesn't exist
env_file = Path(".env")
env_example = Path(".env.example")

if not env_file.exists() and env_example.exists():
    shutil.copy(env_example, env_file)
    print(f"✅ Created .env file from .env.example")
    print(f"⚠️  Please review and update .env with your actual configuration values!")

# ============================================================
# Logging Configuration
# ============================================================
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================
# Application Lifespan
# ============================================================
# 모델 임포트 (SQLAlchemy 메타데이터 등록용)
from app.models import user, sample_post, sample_task, common_code  # noqa

@asynccontextmanager # 🔖 일련번호: 2026021301
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"🚀 Starting API Server on http://localhost:{settings.API_PORT}")
    logger.info(f"📊 Database Type: {settings.DB_TYPE.upper()}")
    
    # Show DB connection info (hide password for PostgreSQL)
    if settings.DB_TYPE.lower() == "sqlite":
        logger.info(f"🗄️  SQLite Path: {settings.SQLITE_DB_PATH}")
    else:
        logger.info(f"🗄️  PostgreSQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # Validate JWT secret
    if settings.JWT_SECRET_KEY == "your-secret-key-change-this-in-production":
        logger.warning("⚠️  Using default JWT_SECRET_KEY! Change this in production!")
    
    # Initialize database (create tables if they don't exist)
    logger.info("📦 Initializing database...")
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API Server...")
    await engine.dispose()
    logger.info("✅ Database connections closed")


# ============================================================
# FastAPI Application
# ============================================================
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ============================================================
# CORS Middleware
# ============================================================
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure via settings.BACKEND_CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Static Files (샘플 HTML 서빙)
# ============================================================
from fastapi.staticfiles import StaticFiles
from pathlib import Path

samples_dir = Path(__file__).parent.parent / "samples"
if samples_dir.exists():
    app.mount("/samples", StaticFiles(directory=str(samples_dir), html=True), name="samples")

# ============================================================
# API Routers
# ============================================================
from app.api.v1 import auth, users, sample_posts, sample_tasks

# 인증 관련
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# 샘플 리소스 (학습용)
app.include_router(
    sample_posts.router, 
    prefix="/api/v1/sample-posts", 
    tags=["sample-posts (공개 리소스 예제)"]
)
app.include_router(
    sample_tasks.router, 
    prefix="/api/v1/sample-tasks", 
    tags=["sample-tasks (인증 필요 리소스 예제)"]
)

# ============================================================
# Exception Handlers
# ============================================================
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions (business logic errors)"""
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# ============================================================
# Health Check
# ============================================================
from sqlalchemy import text

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint with database connectivity test.
    Returns service status and database health.
    """
    health_status = {
        "status": "ok",
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "database": "unknown"
    }
    
    # Check database connectivity
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            health_status["database"] = "healthy"
            break
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

# ============================================================
# Root Endpoint
# ============================================================
@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_TITLE}",
        "docs": "/docs",
        "health": "/health"
    }
