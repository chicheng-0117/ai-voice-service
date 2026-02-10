"""Agent 相关路由"""
from fastapi import APIRouter, Depends
from models import success_response
from api.dependencies import verify_api_token

router = APIRouter(prefix="/api/agents", tags=["agents"])

# 可用Agent列表（可以从配置文件读取）
VALID_AGENTS = {
    "peppa": {"name": "peppa", "display_name": "Peppa Pig"}
}


@router.post("/list", dependencies=[Depends(verify_api_token)])
async def list_agents():
    """
    列出可用的Agent
    
    Returns:
        包含所有可用Agent的列表
    """
    return success_response(
        data={"agents": list(VALID_AGENTS.values())},
        msg="获取Agent列表成功"
    )

