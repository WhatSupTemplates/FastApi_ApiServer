"""
Security utilities for password hashing and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
import base64
import hashlib
import hmac
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import argon2
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from app.core.config import settings


# ============================================================
# Password Hashing
# ============================================================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=65536,
    argon2__parallelism=1,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT Token Management
# ============================================================
ALGORITHM = "HS256"


def _create_token(data: dict, expires_delta: timedelta) -> str:
    """[내부 유틸] 토큰 생성 공통 로직"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    [JWT 액세스 토큰 생성]
    - 설명: 짧은 수명(기본 30분)을 가진 인증용 토큰 발급
    """
    if expires_delta:
        expire_time = expires_delta
    else:
        expire_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES or 30)
    
    return _create_token(data, expire_time)


def create_refresh_token(data: dict) -> str:
    """
    [JWT 리프레시 토큰 생성]
    - 설명: 긴 수명(기본 7일)을 가진 갱신용 토큰 발급
    """
    expire_time = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS or 7)
    return _create_token(data, expire_time)


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary of claims if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================
# One-way Encryption (Search Indexing & Integrity)
# ============================================================
def encrypt_one_way(text: str) -> str:
    """
    [단방향 암호화 / 검색용 해시 생성]
    - 알고리즘: HMAC-SHA256
    - 설명: 입력값이 같으면 항상 같은 암호문이 나오는 특징을 이용
    - 사용처: DB에 암호화되어 저장된 개인정보(예: 전화번호)를 검색할 때 사용 (동일성 비교용)
    """
    if not text:
        return ""
    
    # Use AES_SECRET_KEY for blind indexing if available, otherwise fallback to JWT_SECRET_KEY
    secret_key = getattr(settings, "AES_SECRET_KEY", settings.JWT_SECRET_KEY)
    
    secret_bytes = secret_key.encode('utf-8')
    message_bytes = text.encode('utf-8')
    return hmac.new(secret_bytes, message_bytes, hashlib.sha256).hexdigest()


# ============================================================
# Two-way Encryption (Data Protection)
# ============================================================
def _get_aes_key(secret_key: str) -> bytes:
    """
    [내부 유틸] AES-256 키 생성
    - 설명: 설정 파일의 문자열 키를 AES 알고리즘에 맞는 32바이트 바이너리로 변환
    """
    return hashlib.sha256(secret_key.encode('utf-8')).digest()


def encrypt_two_way(plain_text: str) -> str:
    """
    [양방향 암호화]
    - 알고리즘: AES-256-CBC
    - 설명: 평문을 '키'를 이용해 암호문으로 변환 (복호화 가능)
    - 사용처: 개인정보 등 민감한 데이터를 DB에 저장할 때 사용
    """
    if not plain_text:
        return ""

    if not hasattr(settings, "AES_SECRET_KEY") or not settings.AES_SECRET_KEY:
        # 키가 없으면 암호화 불가, 빈 문자열 반환 (실무에서는 에러 로깅 필요)
        return ""

    # 설정된 AES_SECRET_KEY 사용
    key = _get_aes_key(settings.AES_SECRET_KEY)
    iv = os.urandom(16) # 초기화 벡터 (매번 다른 암호문을 생성하기 위해 사용)
    
    # Padding (암호화 블록 크기에 맞게 데이터 채움)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # IV와 암호문을 합쳐서 Base64 문자열로 반환
    return base64.b64encode(iv + encrypted_data).decode('utf-8')


def decrypt_two_way(encrypted_text: str) -> str:
    """
    [양방향 복호화]
    - 알고리즘: AES-256-CBC
    - 설명: 암호문을 '키'를 이용해 원래 평문으로 복구
    - 사용처: DB에서 꺼낸 암호화된 데이터를 원래 내용으로 확인해야 할 때 사용
    """
    if not encrypted_text:
        return ""

    if not hasattr(settings, "AES_SECRET_KEY") or not settings.AES_SECRET_KEY:
        return ""

    try:
        # Base64 디코딩
        data = base64.b64decode(encrypted_text)
        
        # IV 추출 (앞 16바이트) 및 암호문 분리
        iv = data[:16]
        encrypted_content = data[16:]
        
        key = _get_aes_key(settings.AES_SECRET_KEY)

        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_content) + decryptor.finalize()

        # Unpad (Padding 제거)
        unpadder = padding.PKCS7(128).unpadder()
        plain_data = unpadder.update(padded_data) + unpadder.finalize()
        
        return plain_data.decode('utf-8')
    except Exception as e:
        # 복호화 실패 시 (키가 틀리거나 데이터 손상)
        # print(f"Decryption error: {e}")
        return ""
