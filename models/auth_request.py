"""认证请求基础模型"""
from pydantic import BaseModel


class AuthRequest(BaseModel):
    """需要认证的请求基础模型"""
    token: str  # API访问Token

