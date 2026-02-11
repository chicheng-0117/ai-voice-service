"""认证相关模型"""
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str
    expires_at: str
    user_id: str


class LogoutRequest(BaseModel):
    """登出请求模型"""
    token: str  # API访问Token

