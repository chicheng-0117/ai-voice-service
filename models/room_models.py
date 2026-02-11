"""房间相关模型"""
from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
    """创建房间请求模型"""
    token: str  # API访问Token
    role_name: str  # peppa, george 等


class CreateRoomResponse(BaseModel):
    """创建房间响应模型"""
    room_id: str  # 房间ID（与room_name相同）
    room_name: str  # 房间名称
    token: str  # LiveKit访问Token


class GetRoomInfoRequest(BaseModel):
    """获取房间信息请求模型"""
    token: str  # API访问Token
    room_name: str


class DeleteRoomRequest(BaseModel):
    """删除房间请求模型"""
    token: str  # API访问Token
    room_name: str

