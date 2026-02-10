"""API 依赖项"""
from typing import Optional
from fastapi import HTTPException, Depends, Header
from services.room_service import RoomService
from services.auth_service import AuthService

# 全局房间服务实例（在 main.py 的 lifespan 中初始化）
room_service: Optional[RoomService] = None


def get_room_service() -> RoomService:
    """获取房间服务实例
    
    Returns:
        RoomService实例
        
    Raises:
        HTTPException: 如果服务未初始化
    """
    if not room_service:
        raise HTTPException(status_code=503, detail="服务未初始化")
    return room_service


async def verify_api_token(
    authorization: str = Header(..., description="Bearer token")
) -> dict:
    """
    验证API Token依赖项
    
    从请求头中提取并验证token
    
    Args:
        authorization: Authorization请求头，格式: "Bearer <token>"
        
    Returns:
        Token payload（包含user_id等信息）
        
    Raises:
        HTTPException: Token无效或过期
    """
    # 检查 Authorization 头格式
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="无效的认证格式，请使用: Bearer <token>"
        )
    
    # 提取 token
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token不能为空"
        )
    
    # 验证 token
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token无效或已过期"
        )
    
    return payload
