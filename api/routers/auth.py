"""认证相关路由"""
from fastapi import APIRouter, Header
from models import success_response, error_response
from models.auth_models import LoginRequest, LoginResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(request: LoginRequest):
    """
    登录并获取API访问Token
    
    Token有效期为1小时
    
    Args:
        request: 登录请求
        
    Returns:
        Token信息
    """
    try:
        # 生成token
        token, expires_at = AuthService.generate_token(
            user_id=request.user_id,
            username=request.username
        )
        
        login_data = LoginResponse(
            token=token,
            expires_at=expires_at.isoformat(),
            user_id=request.user_id,
            username=request.username,
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
async def logout(authorization: str = Header(..., description="Bearer token")):
    """
    登出并撤销Token
    
    Args:
        authorization: Authorization请求头
        
    Returns:
        登出结果
    """
    # 提取token
    if not authorization.startswith("Bearer "):
        return error_response(
            code=401,
            msg="无效的认证格式"
        )
    
    token = authorization.replace("Bearer ", "").strip()
    
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

