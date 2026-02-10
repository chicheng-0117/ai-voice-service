"""API 依赖项"""
from typing import Optional
from fastapi import HTTPException, Depends, Header, Query
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
    token: str = Query(..., description="API访问Token")
) -> dict:
    """
    验证API Token依赖项
    
    从查询参数中获取并验证token
    
    Args:
        token: API访问Token（查询参数）
        
    Returns:
        Token payload（包含user_id等信息）
        
    Raises:
        HTTPException: Token无效或过期
    """
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


def get_user_id_from_header(
    user_id: str = Header(..., description="用户ID", alias="userId")
) -> str:
    """
    从请求头获取用户ID
    
    Args:
        user_id: 用户ID（请求头 userId）
        
    Returns:
        用户ID字符串
        
    Raises:
        HTTPException: 如果用户ID为空
    """
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="用户ID不能为空"
        )
    return user_id
