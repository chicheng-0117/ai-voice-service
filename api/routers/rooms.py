"""房间相关路由"""
from fastapi import APIRouter, Depends
from api.dependencies import get_room_service, verify_api_token
from services.room_service import RoomService
from models import (
    success_response,
    error_response,
    CreateRoomRequest,
    CreateRoomResponse,
)

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

# 从 agents router 导入（避免重复）
from api.routers.agents import VALID_AGENTS


@router.post("", dependencies=[Depends(verify_api_token)])
async def create_room(
    request: CreateRoomRequest,
    service: RoomService = Depends(get_room_service)
):
    """
    创建房间
    
    Args:
        request: 创建房间请求
        service: 房间服务实例（依赖注入）
        
    Returns:
        房间信息（房间名称、Agent名称、元数据、创建时间）
    """
    # 验证Agent名称
    if request.agent_name not in VALID_AGENTS:
        return error_response(
            code=400,
            msg=f"无效的Agent名称。可用: {list(VALID_AGENTS.keys())}"
        )
    
    # 创建房间
    try:
        room_info = await service.create_room(
            agent_name=request.agent_name,
            timeout_minutes=request.timeout_minutes,
        )
    except Exception as e:
        return error_response(
            code=500,
            msg=f"创建房间失败: {str(e)}"
        )
    
    room_data = CreateRoomResponse(
        room_name=room_info["room_name"],
        agent_name=room_info["agent_name"],
        metadata=room_info["metadata"],
        created_at=service.active_rooms[room_info["room_name"]]["created_at"].isoformat(),
    )
    
    return success_response(
        data=room_data,
        msg="房间创建成功"
    )


@router.get("/{room_name}", dependencies=[Depends(verify_api_token)])
async def get_room_info(
    room_name: str,
    service: RoomService = Depends(get_room_service)
):
    """
    获取房间信息
    
    Args:
        room_name: 房间名称
        service: 房间服务实例（依赖注入）
        
    Returns:
        房间详细信息
    """
    room_info = service.get_room_info(room_name)
    if not room_info:
        return error_response(
            code=404,
            msg="房间不存在"
        )
    
    room_data = {
        "room_name": room_name,
        "agent_name": room_info["agent_name"],
        "created_at": room_info["created_at"].isoformat(),
        "timeout_minutes": room_info["timeout_minutes"],
    }
    
    return success_response(
        data=room_data,
        msg="获取房间信息成功"
    )


@router.delete("/{room_name}", dependencies=[Depends(verify_api_token)])
async def delete_room(
    room_name: str,
    service: RoomService = Depends(get_room_service)
):
    """
    删除房间
    
    Args:
        room_name: 房间名称
        service: 房间服务实例（依赖注入）
        
    Returns:
        删除结果消息
    """
    try:
        success = await service.delete_room(room_name)
        if success:
            return success_response(
                data={"room_name": room_name},
                msg=f"房间 {room_name} 已删除"
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

