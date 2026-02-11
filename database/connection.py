"""数据库连接配置"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

# 创建 Base 类
Base = declarative_base()

# 数据库连接 URL
def get_database_url() -> str:
    """获取数据库连接 URL"""
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "ai_voice_user")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "ai_voice_db")
    
    # 记录数据库配置（不记录密码）
    logger.info(f"数据库配置: host={host}, port={port}, user={user}, database={database}")
    
    # aiomysql 连接格式: mysql+aiomysql://user:password@host:port/database
    url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    return url


# 创建异步引擎
database_url = get_database_url()
engine = create_async_engine(
    database_url,
    echo=False,  # 设置为 True 可以查看 SQL 日志
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,  # 连接回收时间（秒）
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建表）"""
    from database.models import Agent, Room
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建成功")
        
        # 初始化 Agent 数据
        async with AsyncSessionLocal() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(select(Agent).where(Agent.agent_name == "peppa"))
                agent = result.scalar_one_or_none()
                
                if not agent:
                    peppa_agent = Agent(agent_name="peppa", display_name="Peppa Pig")
                    session.add(peppa_agent)
                    await session.commit()
                    logger.info("初始化 Agent 数据成功")
            except Exception as e:
                logger.error(f"初始化 Agent 数据失败: {e}", exc_info=True)
                await session.rollback()

