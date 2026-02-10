"""房间相关路由"""
import os
import logging
from fastapi import APIRouter, Depends
from api.dependencies import get_room_service, verify_api_token, get_user_id_from_header
from services.room_service import RoomService
from models import (
    success_response,
    error_response,
    CreateRoomRequest,
    CreateRoomResponse,
    GetRoomInfoRequest,
    DeleteRoomRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

# 从 agents router 导入（避免重复）
from api.routers.agents import VALID_AGENTS


@router.post("/create", dependencies=[Depends(verify_api_token)])
async def create_room(
    request: CreateRoomRequest,
    user_id: str = Depends(get_user_id_from_header),
    service: RoomService = Depends(get_room_service)
):
    """
    创建房间并生成Token
    
    Args:
        request: 创建房间请求
        user_id: 用户ID（从请求头 userId 获取）
        service: 房间服务实例（依赖注入）
        
    Returns:
        房间信息（房间ID、房间名称、Token）
    """
    # 验证角色名称
    if request.role_name not in VALID_AGENTS:
        logger.warning(f"无效的角色名称: {request.role_name}, 可用: {list(VALID_AGENTS.keys())}")
        return error_response(
            code=400,
            msg=f"无效的角色名称。可用: {list(VALID_AGENTS.keys())}"
        )
    
    # 创建房间
    try:
        logger.info(f"用户 {user_id} 正在创建房间，角色: {request.role_name}")
        room_info = await service.create_room(
            agent_name=request.role_name,
            timeout_minutes=request.timeout_minutes,
        )
        logger.info(f"房间创建成功: {room_info['room_name']}")
    except Exception as e:
        logger.error(f"创建房间失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"创建房间失败: {str(e)}"
        )
    
    room_name = room_info["room_name"]
    
    # 生成Token
    try:
        logger.info(f"正在为用户 {user_id} 生成房间 {room_name} 的Token")
        token, _ = service.generate_token(
            room_name=room_name,
            user_id=user_id,
        )
        logger.info(f"Token生成成功，房间: {room_name}")
    except Exception as e:
        logger.error(f"生成Token失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"生成Token失败: {str(e)}"
        )
    
    room_data = CreateRoomResponse(
        room_id=room_info["room_id"],  # room_id 与 room_name 相同
        room_name=room_name,
        token=token,
    )
    
    return success_response(
        data=room_data,
        msg="房间创建成功"
    )


@router.post("/info", dependencies=[Depends(verify_api_token)])
async def get_room_info(
    request: GetRoomInfoRequest,
    service: RoomService = Depends(get_room_service)
):
    """
    获取房间信息
    
    Args:
        request: 获取房间信息请求
        service: 房间服务实例（依赖注入）
        
    Returns:
        房间详细信息
    """
    room_info = service.get_room_info(request.room_name)
    if not room_info:
        return error_response(
            code=404,
            msg="房间不存在"
        )
    
    room_data = {
        "room_name": request.room_name,
        "agent_name": room_info["agent_name"],
        "created_at": room_info["created_at"].isoformat(),
        "timeout_minutes": room_info["timeout_minutes"],
    }
    
    return success_response(
        data=room_data,
        msg="获取房间信息成功"
    )


@router.post("/delete", dependencies=[Depends(verify_api_token)])
async def delete_room(
    request: DeleteRoomRequest,
    service: RoomService = Depends(get_room_service)
):
    """
    删除房间
    
    Args:
        request: 删除房间请求
        service: 房间服务实例（依赖注入）
        
    Returns:
        删除结果消息
    """
    try:
        success = await service.delete_room(request.room_name)
        if success:
            return success_response(
                data={"room_name": request.room_name},
                msg=f"房间 {request.room_name} 已删除"
            )
        else:
            return error_response(
                code=500,
                msg="删除房间失败"
            )
    except Exception as e:
        return error_response(
            code=500,
            msg=f"删除房间失败: {str(e)}"
        )

