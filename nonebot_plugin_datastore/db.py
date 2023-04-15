""" 数据库 """
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Callable, Dict, List

from nonebot import get_driver
from nonebot.log import logger
from nonebot.utils import is_coroutine_callable, run_sync
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from .config import plugin_config
from .utils import get_caller_plugin_name

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.engine import AsyncEngine


_engine = None

_pre_db_init_funcs: Dict[str, List] = {}
_post_db_init_funcs = []


def _make_engine() -> "AsyncEngine":
    """创建数据库引擎"""
    url = make_url(plugin_config.datastore_database_url)
    if (
        url.drivername.startswith("sqlite")
        and url.database is not None
        and url.database not in [":memory:", ""]
    ):
        # 创建数据文件夹，防止数据库创建失败
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
    return create_async_engine(url, **engine_options)


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


async def run_funcs(funcs: List[Callable]) -> None:
    """运行所有函数"""
    for func in funcs:
        if is_coroutine_callable(func):
            await func()
        else:
            await run_sync(func)()


async def run_pre_db_init_funcs(plugin: str) -> None:
    """运行数据库初始化前执行的函数"""
    funcs = _pre_db_init_funcs.get(plugin, [])
    if funcs:
        logger.debug(f"运行插件 {plugin} 的数据库初始化前执行的函数")
        await run_funcs(funcs)


async def run_post_db_init_funcs() -> None:
    """运行数据库初始化后执行的函数"""
    if _post_db_init_funcs:
        logger.debug("运行数据库初始化后执行的函数")
        await run_funcs(_post_db_init_funcs)


async def init_db():
    """初始化数据库"""
    from .script.command import upgrade
    from .script.utils import Config, get_plugins

    plugins = get_plugins()
    for plugin in plugins:
        # 执行数据库初始化前执行的函数
        await run_pre_db_init_funcs(plugin)
        # 初始化数据库，升级到最新版本
        logger.debug(f"初始化插件 {plugin} 的数据库")
        config = Config(plugin)
        await upgrade(config, "head")

    logger.info("数据库初始化完成")

    # 执行数据库初始化后执行的函数
    try:
        await run_post_db_init_funcs()
    except Exception as e:
        logger.error(f"数据库初始化后执行的函数出错: {e}")


if plugin_config.datastore_enable_database:
    _engine = _make_engine()
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
