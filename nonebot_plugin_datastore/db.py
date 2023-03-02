""" 数据库 """
import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Callable, Dict, List

from nonebot import get_driver
from nonebot.log import logger
from nonebot.utils import is_coroutine_callable, run_sync
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from nonebot_plugin_datastore.utils import get_caller_plugin_name

from .config import plugin_config

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.engine import AsyncEngine


_engine = None

_pre_db_init_funcs: Dict[str, List] = {}
_post_db_init_funcs = []


def get_engine() -> "AsyncEngine":
    if _engine is None:
        raise ValueError("数据库未启用")
    return _engine


def pre_db_init(func: Callable) -> Callable:
    """数据库初始化前执行的函数"""
    name = get_caller_plugin_name()
    if name not in _pre_db_init_funcs:
        _pre_db_init_funcs[name] = []
    _pre_db_init_funcs[name].append(func)
    return func


def post_db_init(func: Callable) -> Callable:
    """数据库初始化后执行的函数"""
    _post_db_init_funcs.append(func)
    return func


async def init_db():
    """初始化数据库"""
    from .script.utils import run_upgrade

    # 执行数据库初始化前执行的函数
    pre_db_init_funcs = [i for funcs in _pre_db_init_funcs.values() for i in funcs]
    cors = [
        func() if is_coroutine_callable(func) else run_sync(func)()
        for func in pre_db_init_funcs
    ]
    if cors:
        try:
            await asyncio.gather(*cors)
        except Exception as e:
            logger.error("数据库初始化前执行的函数出错")
            raise

    await run_upgrade()

    logger.info("数据库初始化完成")

    # 执行数据库初始化后执行的函数
    cors = [
        func() if is_coroutine_callable(func) else run_sync(func)()
        for func in _post_db_init_funcs
    ]
    if cors:
        try:
            await asyncio.gather(*cors)
        except Exception as e:
            logger.error(f"数据库初始化后执行的函数出错: {e}")


if plugin_config.datastore_enable_database:
    # 创建数据文件夹
    # 防止数据库创建失败
    url = make_url(plugin_config.datastore_database_url)
    if (
        url.drivername.startswith("sqlite")
        and url.database is not None
        and url.database not in [":memory:", ""]
    ):
        database_path = Path(url.database)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"创建数据库文件夹: {database_path.parent}")
    # 创建数据库引擎
    engine_options = {}
    engine_options.update(plugin_config.datastore_engine_options)
    engine_options.setdefault("echo", plugin_config.datastore_database_echo)
    engine_options.setdefault("echo_pool", plugin_config.datastore_database_echo)
    logger.debug(f"数据库连接地址: {plugin_config.datastore_database_url}")
    logger.debug(f"数据库引擎参数: {engine_options}")
    _engine = create_async_engine(url, **engine_options)

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
