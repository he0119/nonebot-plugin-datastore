""" 数据库 """
import os
from typing import AsyncGenerator

from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import plugin_config

engine = None


def get_engine() -> AsyncEngine:
    global engine

    if engine is None:
        raise ValueError("数据库未启用")
    return engine


async def init_db():
    """初始化数据库"""
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("数据库初始化完成")


if plugin_config.datastore_enable_database:
    # 创建数据文件夹
    # 防止数据库创建失败
    os.makedirs(plugin_config.datastore_data_dir, exist_ok=True)
    engine = create_async_engine(
        plugin_config.datastore_database_url,
        echo=plugin_config.datastore_database_echo,
    )

    get_driver().on_startup(init_db)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """需配合 `Depends` 使用

    例: `session: AsyncSession = Depends(get_session)`
    """
    async with AsyncSession(get_engine()) as session:
        yield session


def create_session() -> AsyncSession:
    """创建一个新的 session"""
    return AsyncSession(get_engine())
