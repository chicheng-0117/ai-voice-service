"""Agent 相关路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import success_response
from models.agent_models import ListAgentsRequest
from api.dependencies import verify_api_token
from database import get_db
from database.repositories import AgentRepository

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/list")
async def list_agents(
    request: ListAgentsRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    列出可用的Agent
    
    Args:
        request: 包含 token 的请求
        db: 数据库会话
        
    Returns:
        包含所有可用Agent的列表
    """
    try:
        agents = await AgentRepository.get_all(db)
        agents_data = [
            {
                "name": agent.agent_name,
                "display_name": agent.display_name
            }
            for agent in agents
        ]
        return success_response(
            data={"agents": agents_data},
            msg="获取Agent列表成功"
        )
    except Exception as e:
        return success_response(
            data={"agents": []},
            msg=f"获取Agent列表失败: {str(e)}"
        )

