from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
from app.core.config import settings
from redis import Redis
import re

class TokenData(BaseModel):
    username: str
    exp: datetime
    token_type: str

class AuthService:
    def __init__(self, redis_client: Redis):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redis_client = redis_client
        self.password_pattern = re.compile(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def validate_password_policy(self, password: str) -> bool:
        """Validate password against security policy."""
        if not self.password_pattern.match(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain at least one letter, one number, and one special character"
            )
        return True

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "token_type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self, username: str) -> str:
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {"sub": username, "exp": expire, "token_type": "refresh"}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        
        # Store refresh token in Redis with expiration
        self.redis_client.setex(
            f"refresh_token:{username}",
            timedelta(days=7).total_seconds(),
            encoded_jwt
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            exp: datetime = datetime.fromtimestamp(payload.get("exp"))
            token_type: str = payload.get("token_type")
            
            if username is None or exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
                
            return TokenData(username=username, exp=exp, token_type=token_type)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        token_data = self.verify_token(refresh_token)
        if token_data.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        # Verify refresh token exists in Redis
        stored_token = self.redis_client.get(f"refresh_token:{token_data.username}")
        if not stored_token or stored_token.decode() != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
            
        # Create new access token
        access_token = self.create_access_token({"sub": token_data.username})
        return {"access_token": access_token, "token_type": "bearer"}

    def revoke_refresh_token(self, username: str) -> None:
        """Revoke a user's refresh token."""
        self.redis_client.delete(f"refresh_token:{username}")

    def invalidate_all_sessions(self, username: str) -> None:
        """Invalidate all active sessions for a user."""
        self.revoke_refresh_token(username)
        # Add additional session cleanup logic here if needed