""" 数据库 """
import os
from typing import AsyncGenerator

from nonebot import get_driver
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import plugin_config

if plugin_config.datastore_enable_database:
    # 创建数据文件夹
    # 防止数据库创建失败
    os.makedirs(plugin_config.datastore_data_dir, exist_ok=True)
    engine = create_async_engine(
        plugin_config.datastore_database_url,
        echo=plugin_config.datastore_database_echo,
    )

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    get_driver().on_startup(init_db)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not plugin_config.datastore_enable_database:
        raise ValueError("Database is not enabled.")

    async with AsyncSession(engine) as session:
        yield session
