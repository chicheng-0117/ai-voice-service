"""认证相关模型"""
from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录请求模型"""
    user_id: str
    username: Optional[str] = None


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str
    expires_at: str
    user_id: str
    username: Optional[str] = None

