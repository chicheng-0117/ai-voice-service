"""独立的API服务，负责房间管理和Token生成"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.room_service import RoomService
from api.dependencies import room_service
from api.routers import agents, rooms, tokens, health, auth
from models import success_response

# 加载环境变量
load_dotenv(".env.local")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    global room_service
    try:
        room_service = RoomService()
        print("✓ RoomService 初始化成功")
    except ValueError as e:
        print(f"✗ 环境变量配置错误: {e}")
        print("请检查 .env.local 文件是否已正确配置。")
        raise
    except Exception as e:
        print(f"✗ RoomService 初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    if room_service:
        await room_service.close()
        print("✓ RoomService 已关闭")


app = FastAPI(
    title="LiveKit Multi-Agent API Server",
    description="基于 LiveKit 的多 Agent 语音助手系统 API 服务",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)  # 认证路由（不需要认证）
app.include_router(agents.router)  # 需要认证
app.include_router(rooms.router)  # 需要认证
app.include_router(tokens.router)  # 需要认证
app.include_router(health.router)  # 健康检查（不需要认证）


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return success_response(
        data={
            "message": "LiveKit Multi-Agent API Server",
            "version": "0.1.0",
            "docs": "/docs"
        },
        msg="API服务运行正常"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

