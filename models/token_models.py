"""Token相关模型"""
from typing import Optional
from pydantic import BaseModel


class GenerateTokenRequest(BaseModel):
    """生成Token请求模型"""
    room_name: str
    can_publish: bool = True
    can_subscribe: bool = True


class GenerateTokenResponse(BaseModel):
    """生成Token响应模型"""
    token: str
    ws_url: str
    room_name: str
    user_id: str

