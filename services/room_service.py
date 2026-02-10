"""房间管理服务"""
import os
import uuid
import asyncio
import warnings
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from livekit import api

logger = logging.getLogger(__name__)


class RoomService:
    """房间管理服务类"""
    
    def __init__(self):
        """初始化房间服务
        
        使用 LiveKitAPI 自动从环境变量读取配置：
        - LIVEKIT_URL
        - LIVEKIT_API_KEY
        - LIVEKIT_API_SECRET
        """
        # 验证环境变量
        self._validate_env_vars()
        
        # 使用 LiveKitAPI，会自动从环境变量读取配置
        # LiveKitAPI 需要 HTTPS URL，而不是 WSS URL
        livekit_url = os.getenv("LIVEKIT_URL", "")
        if livekit_url.startswith("wss://"):
            # 将 wss:// 转换为 https://
            api_url = livekit_url.replace("wss://", "https://")
            self.lkapi = api.LiveKitAPI(url=api_url)
        else:
            self.lkapi = api.LiveKitAPI()
        
        self.active_rooms: Dict[str, dict] = {}
    
    def _validate_env_vars(self):
        """验证必需的环境变量"""
        required_vars = {
            "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
            "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY"),
            "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET"),
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            raise ValueError(
                f"缺少必需的环境变量: {', '.join(missing)}. "
                f"请检查 .env.local 文件是否已正确配置。"
            )
        
        # 检查 API Secret 长度（警告）
        api_secret = required_vars["LIVEKIT_API_SECRET"]
        if len(api_secret.encode('utf-8')) < 32:
            warnings.warn(
                f"LIVEKIT_API_SECRET 长度 ({len(api_secret)} 字节) 低于推荐的最小长度 (32 字节)。"
                f"这可能导致 JWT 密钥强度不足。建议使用更长的 API Secret。",
                UserWarning
            )
        
        # 检查 URL 格式
        url = required_vars["LIVEKIT_URL"]
        if not url.startswith(("wss://", "ws://", "https://")):
            raise ValueError(
                f"LIVEKIT_URL 格式不正确: {url}. "
                f"应该以 wss:// 或 https:// 开头。"
            )
        
        # 检查是否是示例 URL
        if "your-livekit-server.com" in url or "example.com" in url:
            raise ValueError(
                f"LIVEKIT_URL 使用的是示例 URL: {url}. "
                f"请配置实际的 LiveKit 服务器地址。"
            )
    
    async def create_room(
        self, 
        agent_name: str, 
        timeout_minutes: int = 60
    ) -> dict:
        """
        创建房间，在元数据中指定Agent
        
        Args:
            agent_name: Agent名称（如 peppa, george）
            timeout_minutes: 房间超时时间（分钟），默认60分钟
            
        Returns:
            包含房间信息的字典
            
        Raises:
            Exception: 创建房间失败时抛出异常
        """
        # 房间命名规则: room-{agent_name}-{random_id}
        room_name = f"room-{agent_name}-{uuid.uuid4().hex[:8]}"
        
        try:
            # 创建房间，在元数据中指定Agent名称
            # 使用 CreateRoomRequest 作为参数
            room = await self.lkapi.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    metadata=f"agent:{agent_name}",  # 关键：通过元数据传递Agent信息
                )
            )
            # 记录房间信息（使用 room_name 作为 key）
            self.active_rooms[room_name] = {
                "room_name": room_name,
                "room_id": room.sid,  # 保存 room_id 仅用于响应，不用于操作
                "agent_name": agent_name,
                "created_at": datetime.now(),
                "timeout_minutes": timeout_minutes,
            }
            
            # 启动定时关闭任务
            asyncio.create_task(
                self._schedule_room_close(room_name, timeout_minutes)
            )
            
            return {
                "room_id": room.sid,  # 返回 room_id 供客户端使用（如果需要）
                "room_name": room_name,
                "agent_name": agent_name,
                "metadata": room.metadata,
            }
        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误信息
            if "getaddrinfo failed" in error_msg or "Cannot connect" in error_msg:
                raise Exception(
                    f"无法连接到 LiveKit 服务器。"
                    f"请检查 LIVEKIT_URL 是否正确: {os.getenv('LIVEKIT_URL')}"
                )
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(
                    "LiveKit API 认证失败。请检查 LIVEKIT_API_KEY 和 LIVEKIT_API_SECRET 是否正确。"
                )
            else:
                raise Exception(f"创建房间失败: {error_msg}")
    
    async def _schedule_room_close(self, room_name: str, timeout_minutes: int):
        """
        定时关闭房间
        
        Args:
            room_name: 房间名称
            timeout_minutes: 超时时间（分钟）
        """
        await asyncio.sleep(timeout_minutes * 60)
        try:
            # 检查房间是否还存在
            if room_name not in self.active_rooms:
                logger.warning(f"房间 {room_name} 不存在于 active_rooms 中，跳过关闭")
                return
            
            # 使用 room_name 删除房间
            await self.lkapi.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            if room_name in self.active_rooms:
                del self.active_rooms[room_name]
            logger.info(f"房间 {room_name} 已定时关闭")
        except Exception as e:
            logger.error(f"关闭房间失败: {room_name}, 错误: {e}", exc_info=True)
    
    def generate_token(
        self, 
        room_name: str, 
        user_id: Optional[str] = None,
        can_publish: bool = True,
        can_subscribe: bool = True,
    ) -> tuple[str, str]:
        """
        生成用户Token
        
        Args:
            room_name: 房间名称
            user_id: 用户ID，如果未提供则自动生成
            can_publish: 是否允许发布音视频
            can_subscribe: 是否允许订阅音视频
            
        Returns:
            (token, user_id) 元组，包含JWT Token字符串和用户ID
        """
        user_id = user_id or f"user-{uuid.uuid4().hex[:8]}"
        
        # 使用链式调用，AccessToken 会自动从环境变量读取 API Key 和 Secret
        # 如果环境变量未设置，可以显式传递：
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        token = (
            api.AccessToken(api_key=api_key, api_secret=api_secret)
            .with_identity(user_id)
            .with_name(f"User-{user_id[:8]}")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=can_publish,
                    can_subscribe=can_subscribe,
                )
            )
        )
        
        return token.to_jwt(), user_id
    
    async def delete_room(self, room_name: str) -> bool:
        """
        删除房间
        
        Args:
            room_name: 房间名称
            
        Returns:
            是否删除成功
        """
        try:
            # 检查房间是否存在
            if room_name not in self.active_rooms:
                logger.warning(f"房间 {room_name} 不存在于 active_rooms 中")
                return False
            
            # 使用 room_name 删除房间
            await self.lkapi.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            
            # 从 active_rooms 中删除
            if room_name in self.active_rooms:
                del self.active_rooms[room_name]
            logger.info(f"房间 {room_name} 已删除")
            return True
        except Exception as e:
            logger.error(f"删除房间失败: {room_name}, 错误: {e}", exc_info=True)
            return False
    
    def get_room_info(self, room_name: str) -> Optional[dict]:
        """
        获取房间信息
        
        Args:
            room_name: 房间名称
            
        Returns:
            房间信息字典，如果房间不存在则返回None
        """
        # 直接使用 room_name 作为 key 查找
        return self.active_rooms.get(room_name)
    
    async def close(self):
        """
        关闭 LiveKitAPI 连接
        
        在应用关闭时调用此方法以正确清理资源
        """
        if self.lkapi:
            await self.lkapi.aclose()

