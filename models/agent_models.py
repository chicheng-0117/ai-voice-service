"""Agent相关模型"""
from pydantic import BaseModel


class ListAgentsRequest(BaseModel):
    """列出Agent请求模型"""
    token: str  # API访问Token

