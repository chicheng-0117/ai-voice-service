"""统一API响应模型"""
from typing import Optional, TypeVar, Generic, Any
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式
    
    所有API接口都使用此格式返回数据：
    - code: HTTP状态码
    - success: 是否成功
    - msg: 消息描述
    - data: 响应数据（泛型）
    """
    code: int
    success: bool
    msg: str
    data: Optional[T] = None


def success_response(data: Any = None, msg: str = "操作成功") -> ApiResponse:
    """创建成功响应
    
    Args:
        data: 响应数据
        msg: 成功消息
        
    Returns:
        ApiResponse实例
    """
    return ApiResponse(code=200, success=True, msg=msg, data=data)


def error_response(code: int, msg: str) -> ApiResponse:
    """创建错误响应
    
    Args:
        code: 错误状态码
        msg: 错误消息
        
    Returns:
        ApiResponse实例
    """
    return ApiResponse(code=code, success=False, msg=msg, data=None)

