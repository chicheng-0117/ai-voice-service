"""Token 相关路由"""
import os
from fastapi import APIRouter, Depends
from api.dependencies import get_room_service, verify_api_token, get_user_id_from_header
from services.room_service import RoomService
from models import (
    success_response,
    error_response,
    GenerateTokenRequest,
    GenerateTokenResponse,
)

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@router.post("")
async def generate_token(
    request: GenerateTokenRequest,
    user_id: str = Depends(get_user_id_from_header),
    service: RoomService = Depends(get_room_service),
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    生成访问Token

    Args:
        request: 生成Token请求（包含 room_name）
        user_id: 用户ID（从请求头 userId 获取）
        service: 房间服务实例（依赖注入）
        
    Returns:
        Token信息（token、WebSocket URL、房间名称、用户ID）
    """
    # 验证房间是否存在
    room_info = service.get_room_info(request.room_name)
    if not room_info:
        return error_response(
            code=404,
            msg=f"房间不存在: {request.room_name}。请先创建房间。"
        )
    
    try:
        # 生成Token（使用请求头中的 user_id）
        token, actual_user_id = service.generate_token(
            room_name=request.room_name,
            user_id=user_id,
            can_publish=request.can_publish,
            can_subscribe=request.can_subscribe,
        )
    except Exception as e:
        return error_response(
            code=500,
            msg=f"生成Token失败: {str(e)}"
        )
    
    # 获取WebSocket URL
    ws_url = os.getenv("LIVEKIT_URL")
    if not ws_url:
        return error_response(
            code=500,
            msg="LIVEKIT_URL 环境变量未配置"
        )
    
    token_data = GenerateTokenResponse(
        token=token,
        ws_url=ws_url,
        room_name=request.room_name,
        user_id=actual_user_id,
    )
    
    return success_response(
        data=token_data,
        msg="Token生成成功"
    )

