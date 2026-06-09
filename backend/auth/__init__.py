"""
Authentication and authorization utilities.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
    """
    Create a JWT access token.
    
    Returns:
        (token, expires_at) tuple
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt, expire


def create_refresh_token(data: dict) -> tuple[str, datetime]:
    """
    Create a JWT refresh token (longer expiration).
    
    Returns:
        (token, expires_at) tuple
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt, expire


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Returns:
        Decoded token payload, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None


def create_api_key_token(user_id: str, key_name: str) -> str:
    """
    Create an API key (long-lived token).
    """
    data = {
        "user_id": user_id,
        "key_name": key_name,
        "type": "api_key"
    }
    # API keys don't expire unless explicitly set
    token = jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return token


def verify_api_key(token: str) -> Optional[dict]:
    """Verify an API key token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "api_key":
            return None
        return payload
    except JWTError:
        return None


def extract_token_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extract bearer token from Authorization header.
    Expected format: "Bearer <token>"
    """
    if not authorization_header:
        return None
    
    try:
        scheme, token = authorization_header.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None
