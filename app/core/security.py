import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pw_bytes = password.encode('utf-8')
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hashed password."""
    pw_bytes = plain_password.encode('utf-8')
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
    try:
        return bcrypt.checkpw(pw_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token for a given subject (user ID or email)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
