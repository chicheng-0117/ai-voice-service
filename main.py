"""独立的API服务，负责房间管理和Token生成"""
import logging
import traceback
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# ⚠️ 必须在所有其他导入之前加载环境变量
# 因为 database.connection 在模块导入时就会读取环境变量
load_dotenv(".env.local")

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException

from services.room_service import RoomService
from api import dependencies
from api.routers import agents, rooms, health, auth
from models import success_response, error_response, ApiResponse
from database import init_db

# 配置日志
import sys

# 检测是否支持颜色（Windows 10+ 支持，但需要检测）
def supports_color():
    """检测终端是否支持颜色"""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # 检查是否在支持颜色的终端中
            return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        except:
            return False
    else:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def __init__(self, *args, use_color=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_color = use_color and supports_color()
    
    def format(self, record):
        if self.use_color:
            log_color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{log_color}{record.levelname:8s}{self.RESET}"
            record.name = f"\033[90m{record.name:20s}\033[0m"  # 灰色模块名
        else:
            record.levelname = f"{record.levelname:8s}"
            record.name = f"{record.name:20s}"
        return super().format(record)

# 创建格式化器
formatter = ColoredFormatter(
    fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    use_color=True
)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 清除现有的处理器
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    try:
        # 初始化数据库
        logger.info("正在初始化数据库...")
        await init_db()
        logger.info("✓ 数据库初始化成功")
        
        # 初始化 RoomService
        logger.info("正在初始化 RoomService...")
        room_service_instance = RoomService()
        # 设置到 dependencies 模块中，供依赖注入使用
        dependencies.room_service = room_service_instance
        logger.info("✓ RoomService 初始化成功")
    except ValueError as e:
        logger.error(f"✗ 环境变量配置错误: {e}")
        logger.error("请检查 .env.local 文件是否已正确配置。")
        raise
    except Exception as e:
        logger.error(f"✗ 初始化失败: {e}")
        logger.error(traceback.format_exc())
        raise
    
    yield
    
    # 关闭时清理
    if dependencies.room_service:
        logger.info("正在关闭 RoomService...")
        await dependencies.room_service.close()
        dependencies.room_service = None
        logger.info("✓ RoomService 已关闭")


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


# 全局异常处理器
@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """处理 HTTPException，统一返回格式"""
    logger.error(
        f"HTTP异常: {exc.status_code} - {exc.detail} | "
        f"路径: {request.url.path} | 方法: {request.method}"
    )
    
    response = error_response(
        code=exc.status_code,
        msg=str(exc.detail)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误，统一返回格式"""
    errors = exc.errors()
    error_msg = "; ".join([f"{err['loc']}: {err['msg']}" for err in errors])
    
    logger.error(
        f"请求验证错误: {error_msg} | "
        f"路径: {request.url.path} | 方法: {request.method}"
    )
    
    response = error_response(
        code=400,
        msg=f"请求参数验证失败: {error_msg}"
    )
    return JSONResponse(
        status_code=400,
        content=response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常，统一返回格式"""
    error_traceback = traceback.format_exc()
    logger.error(
        f"未捕获的异常: {type(exc).__name__} - {str(exc)} | "
        f"路径: {request.url.path} | 方法: {request.method}\n"
        f"堆栈跟踪:\n{error_traceback}"
    )
    
    response = error_response(
        code=500,
        msg=f"服务器内部错误: {str(exc)}"
    )
    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )

# 注册路由
app.include_router(auth.router)  # 认证路由（不需要认证）
app.include_router(agents.router)  # 需要认证
app.include_router(rooms.router)  # 需要认证
# app.include_router(tokens.router)  # 已移除，token在create_room接口中返回
app.include_router(health.router)  # 健康检查（不需要认证）


@app.post("/")
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
    import sys
    import asyncio
    
    # 检查是否启用 debug 模式
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv
    
    # 尝试使用 uvicorn.run()，如果失败则使用手动启动方式（兼容 PyCharm 调试器）
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=debug_mode,  # debug 模式下自动重载
            log_level="debug" if debug_mode else "info",  # debug 模式下显示详细日志
        )
    except TypeError as e:
        # 如果遇到 loop_factory 错误（PyCharm 调试器问题），使用备用方法
        if "loop_factory" in str(e):
            print("检测到 PyCharm 调试器兼容性问题，使用备用启动方式...")
            config = uvicorn.Config(
                "main:app",  # 使用字符串形式
                host="0.0.0.0",
                port=8000,
                reload=False,  # 调试器模式下禁用自动重载
                log_level="debug" if debug_mode else "info",
            )
            server = uvicorn.Server(config)
            # 使用 asyncio.run() 而不是 server.run()，避免 loop_factory 参数问题
            asyncio.run(server.serve())
        else:
            raise

