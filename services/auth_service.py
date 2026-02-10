"""API认证服务"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt

# Token 配置
TOKEN_SECRET_KEY = os.getenv("API_TOKEN_SECRET", secrets.token_urlsafe(32))
TOKEN_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1  # Token 有效期 1 小时

# 存储 token 的字典（生产环境应该使用 Redis 或数据库）
# key: token_hash, value: {user_id, expires_at, created_at}
token_store: Dict[str, dict] = {}


class AuthService:
    """API认证服务类"""
    
    @staticmethod
    def generate_token(user_id: str) -> tuple[str, datetime]:
        """
        生成API访问Token
        
        Args:
            user_id: 用户ID
            
        Returns:
            (token, expires_at) 元组
        """
        # Token 过期时间
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=TOKEN_EXPIRE_HOURS)
        
        # 创建 JWT payload（exp 和 iat 需要是时间戳）
        payload = {
            "user_id": user_id,
            "exp": int(expires_at.timestamp()),
            "iat": int(now.timestamp()),
            "type": "api_access"
        }
        
        # 生成 JWT token
        token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
        
        # 存储 token（用于验证和撤销）
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_store[token_hash] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": now,
        }
        
        return token, expires_at
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        验证Token
        
        Args:
            token: JWT token字符串
            
        Returns:
            如果验证成功返回payload字典，否则返回None
        """
        try:
            # 验证 token 是否在存储中（检查是否被撤销）
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash not in token_store:
                return None
            
            # 验证 token 是否过期
            stored_info = token_store[token_hash]
            now = datetime.now(timezone.utc)
            if now > stored_info["expires_at"]:
                # 清理过期的 token
                del token_store[token_hash]
                return None
            
            # 解码和验证 JWT
            payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
            
            # 验证 token 类型
            if payload.get("type") != "api_access":
                return None
            
            return payload
            
        except JWTError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def revoke_token(token: str) -> bool:
        """
        撤销Token（登出时使用）
        
        Args:
            token: 要撤销的token
            
        Returns:
            是否撤销成功
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash in token_store:
                del token_store[token_hash]
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def cleanup_expired_tokens():
        """清理过期的token"""
        now = datetime.now(timezone.utc)
        expired_tokens = [
            token_hash for token_hash, info in token_store.items()
            if now > info["expires_at"]
        ]
        for token_hash in expired_tokens:
            del token_store[token_hash]

