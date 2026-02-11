"""房间相关路由"""
import os
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_room_service, verify_api_token, get_user_id_from_header
from database import get_db
from services.room_service import RoomService
from database.repositories import AgentRepository
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


@router.post("/create")
async def create_room(
    request: CreateRoomRequest,
    user_id: str = Depends(get_user_id_from_header),
    service: RoomService = Depends(get_room_service),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    创建房间并生成Token
    
    Args:
        request: 创建房间请求
        user_id: 用户ID（从请求头 userId 获取）
        service: 房间服务实例（依赖注入）
        db: 数据库会话
        
    Returns:
        房间信息（房间ID、房间名称、Token）
    """
    # 验证角色名称（从数据库获取）
    try:
        agent = await AgentRepository.get_by_name(db, request.role_name)
        if not agent:
            logger.warning(f"无效的角色名称: {request.role_name}")
            return error_response(
                code=400,
                msg=f"无效的角色名称: {request.role_name}"
            )
    except Exception as e:
        logger.error(f"查询Agent失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"查询Agent失败: {str(e)}"
        )
    
    # 创建房间（会生成 room_name）
    try:
        logger.info(f"用户 {user_id} 正在创建房间，角色: {request.role_name}")
        room_info = await service.create_room(
            agent_name=request.role_name,
            user_id=user_id,
            room_token="",  # 先传空，后面会更新
            db=db,
        )
        logger.info(f"房间创建成功: {room_info['room_name']}")
    except Exception as e:
        logger.error(f"创建房间失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"创建房间失败: {str(e)}"
        )
    
    room_name = room_info["room_name"]
    
    # 生成Token（使用实际的房间名）
    try:
        logger.info(f"正在为用户 {user_id} 生成房间 {room_name} 的Token")
        token, _ = service.generate_token(
            room_name=room_name,
            user_id=user_id,
        )
        
        # 更新数据库中的 token（用户加入时间由 Agent 端记录）
        from database.repositories import RoomRepository
        await RoomRepository.update_token(db, room_name, token)
        await db.commit()
        
        logger.info(f"Token生成成功，房间: {room_name}")
    except Exception as e:
        logger.error(f"生成Token失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"生成Token失败: {str(e)}"
        )
    
    room_data = CreateRoomResponse(
        room_id=room_info["room_id"],
        room_name=room_name,
        token=token,
    )
    
    return success_response(
        data=room_data,
        msg="房间创建成功"
    )


@router.post("/info")
async def get_room_info(
    request: GetRoomInfoRequest,
    service: RoomService = Depends(get_room_service),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    获取房间信息
    
    Args:
        request: 获取房间信息请求
        service: 房间服务实例（依赖注入）
        db: 数据库会话
        
    Returns:
        房间详细信息
    """
    room_info = await service.get_room_info(request.room_name, db)
    if not room_info:
        return error_response(
            code=404,
            msg="房间不存在"
        )
    
    room_data = {
        "room_name": room_info["room_name"],
        "agent_name": room_info["agent_name"],
        "status": room_info["status"],
        "created_at": room_info["created_at"].isoformat() if room_info["created_at"] else None,
        "user_joined_at": room_info["user_joined_at"].isoformat() if room_info["user_joined_at"] else None,
        "user_left_at": room_info["user_left_at"].isoformat() if room_info["user_left_at"] else None,
        "chat_duration": room_info["chat_duration"],
        "timeout_minutes": room_info["timeout_minutes"],
    }
    
    return success_response(
        data=room_data,
        msg="获取房间信息成功"
    )


@router.post("/delete")
async def delete_room(
    request: DeleteRoomRequest,
    service: RoomService = Depends(get_room_service),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    删除房间（只删除 LiveKit 房间，不删除数据库记录，只更新状态为 closed）
    
    Args:
        request: 删除房间请求
        service: 房间服务实例（依赖注入）
        db: 数据库会话
        
    Returns:
        删除结果消息
    """
    try:
        # 获取房间信息
        from database.repositories import RoomRepository
        room = await RoomRepository.get_by_name(db, request.room_name)
        if not room:
            return error_response(
                code=404,
                msg="房间不存在"
            )
        
        # 如果房间已经是关闭状态，直接返回
        if room.status == "closed":
            return success_response(
                data={"room_name": request.room_name, "status": "closed"},
                msg=f"房间 {request.room_name} 已经是关闭状态"
            )
        
        # 删除房间（会删除 LiveKit 房间并更新数据库状态）
        success = await service.delete_room(request.room_name, db)
        if success:
            # 重新获取房间信息以获取最新的聊天时长
            room = await RoomRepository.get_by_name(db, request.room_name)
            chat_duration = room.chat_duration if room else 0
            
            return success_response(
                data={
                    "room_name": request.room_name,
                    "status": "closed",
                    "chat_duration": chat_duration
                },
                msg=f"房间 {request.room_name} 已关闭"
            )
        else:
            return error_response(
                code=500,
                msg="关闭房间失败"
            )
    except Exception as e:
        await db.rollback()
        logger.error(f"关闭房间失败: {str(e)}", exc_info=True)
        return error_response(
            code=500,
            msg=f"关闭房间失败: {str(e)}"
        )

