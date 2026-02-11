"""Agent 相关路由"""
from fastapi import APIRouter, Depends
from models import success_response
from models.agent_models import ListAgentsRequest
from api.dependencies import verify_api_token

router = APIRouter(prefix="/api/agents", tags=["agents"])

# 可用Agent列表（可以从配置文件读取）
VALID_AGENTS = {
    "peppa": {"name": "peppa", "display_name": "Peppa Pig"}
}


@router.post("/list")
async def list_agents(
    request: ListAgentsRequest,
    _: dict = Depends(verify_api_token)  # 验证 token，但不使用返回值
):
    """
    列出可用的Agent
    
    Args:
        request: 包含 token 的请求
        
    Returns:
        包含所有可用Agent的列表
    """
    return success_response(
        data={"agents": list(VALID_AGENTS.values())},
        msg="获取Agent列表成功"
    )

