"""认证相关路由"""
from fastapi import APIRouter, Query, Depends
from api.dependencies import get_user_id_from_header
from models import success_response, error_response
from models.auth_models import LoginResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(user_id: str = Depends(get_user_id_from_header)):
    """
    登录并获取API访问Token
    
    Token有效期为1小时
    
    Args:
        user_id: 用户ID（从请求头 userId 获取）
        
    Returns:
        Token信息
    """
    try:
        # 生成token
        token, expires_at = AuthService.generate_token(
            user_id=user_id
        )
        
        login_data = LoginResponse(
            token=token,
            expires_at=expires_at.isoformat(),
            user_id=user_id,
        )
        
        return success_response(
            data=login_data,
            msg="登录成功"
        )
    except Exception as e:
        return error_response(
            code=500,
            msg=f"登录失败: {str(e)}"
        )


@router.post("/logout")
async def logout(token: str = Query(..., description="API访问Token")):
    """
    登出并撤销Token
    
    Args:
        token: API访问Token（查询参数）
        
    Returns:
        登出结果
    """
    if not token:
        return error_response(
            code=401,
            msg="Token不能为空"
        )
    
    # 撤销token
    success = AuthService.revoke_token(token)
    if success:
        return success_response(
            data=None,
            msg="登出成功"
        )
    else:
        return error_response(
            code=400,
            msg="Token无效或已过期"
        )

