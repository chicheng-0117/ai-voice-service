"""房间相关模型"""
from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
    """创建房间请求模型"""
    agent_name: str  # peppa, george 等
    timeout_minutes: int = 60  # 房间超时时间（分钟）


class CreateRoomResponse(BaseModel):
    """创建房间响应模型"""
    room_name: str
    agent_name: str
    metadata: str
    created_at: str

