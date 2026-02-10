"""健康检查路由"""
from fastapi import APIRouter, Depends
from api.dependencies import get_room_service
from services.room_service import RoomService
from models import success_response

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(service: RoomService = Depends(get_room_service)):
    """
    健康检查端点
    
    Args:
        service: 房间服务实例（依赖注入）
        
    Returns:
        服务健康状态和活跃房间数量
    """
    return success_response(
        data={
            "status": "healthy",
            "active_rooms": len(service.active_rooms)
        },
        msg="服务运行正常"
    )

