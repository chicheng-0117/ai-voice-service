"""API 依赖项"""
import json
from typing import Optional
from fastapi import HTTPException, Depends, Header, Request
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


async def verify_api_token(request: Request) -> dict:
    """
    验证API Token依赖项
    
    从请求体中获取并验证token
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        Token payload（包含user_id等信息）
        
    Raises:
        HTTPException: Token无效或过期
    """
    try:
        # 读取请求体
        body_bytes = await request.body()
        if not body_bytes:
            raise HTTPException(
                status_code=400,
                detail="请求体不能为空，请在请求体中提供 token 字段"
            )
        
        # 解析 JSON
        body = json.loads(body_bytes.decode())
        token = body.get("token")
        
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Token不能为空，请在请求体中提供 token 字段"
            )
        
        # 验证 token
        payload = AuthService.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Token无效或已过期"
            )
        
        # 将请求体缓存到 request.state，以便后续的请求模型可以正常解析
        # 注意：FastAPI 的请求体只能读取一次，所以需要重新设置
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        
        # 重新设置 _receive 方法，使请求体可以再次读取
        request._receive = receive
        
        return payload
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="请求体必须是有效的 JSON 格式，且包含 token 字段"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token验证失败: {str(e)}"
        )


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
