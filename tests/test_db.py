from pathlib import Path

import pytest
from nonebot import require
from nonebug import App
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool, QueuePool

from .utils import clear_plugins, make_fake_event, make_fake_message


async def test_db(app: App):
    """测试数据库"""
    from sqlalchemy import select

    from nonebot_plugin_datastore.db import create_session, init_db

    require("tests.example.plugin1")
    from .example.plugin1 import Example, test

    await init_db()

    async with create_session() as session:
        statement = select(Example)
        example = (await session.scalars(statement)).one()
        assert example.message == "post"

    async with create_session() as session:
        session.add(Example(message="test"))
        await session.commit()

    async with create_session() as session:
        statement = select(Example)
        examples = (await session.scalars(statement)).all()
        assert len(examples) == 2
        assert examples[1].message == "test"

    message = make_fake_message()("/test")
    event = make_fake_event(_message=message)()

    async with app.test_matcher(test) as ctx:
        bot = ctx.create_bot()

        ctx.receive_event(bot, event)

    async with create_session() as session:
        statement = select(Example)
        examples = (await session.scalars(statement)).all()
        assert len(examples) == 3
        assert examples[2].message == "matcher"


@pytest.mark.parametrize(
    "app",
    [pytest.param({"datastore_enable_database": "false"}, id="disable_db")],
    indirect=True,
)
async def test_disable_db(app: App):
    """测试禁用数据库"""
    from nonebot_plugin_datastore import create_session

    with pytest.raises(ValueError, match="数据库未启用"):
        create_session()


async def test_default_db_url(nonebug_init: None):
    """测试默认数据库地址"""
    import nonebot

    clear_plugins()

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_datastore")

    from nonebot_plugin_datastore.config import plugin_config

    assert (
        plugin_config.datastore_database_url
        == f"sqlite+aiosqlite:///{plugin_config.datastore_data_dir / 'data.db'}"
    )


async def test_post_db_init_error(app: App):
    """数据库初始化后执行函数错误"""
    from nonebot_plugin_datastore.db import init_db, post_db_init

    @post_db_init
    async def _():
        raise Exception("test")

    await init_db()


async def test_pre_db_init_error(app: App):
    """数据库初始化前执行函数错误"""
    from nonebot_plugin_datastore.db import init_db

    require("tests.example.pre_db_init_error")

    with pytest.raises(OperationalError):
        await init_db()


@pytest.mark.parametrize(
    "app",
    [pytest.param({"datastore_engine_options": {"pool_recycle": 7200}}, id="options")],
    indirect=True,
)
async def test_engine_options(app: App):
    """测试引擎配置"""
    from nonebot_plugin_datastore.config import plugin_config
    from nonebot_plugin_datastore.db import get_engine

    assert plugin_config.datastore_engine_options == {"pool_recycle": 7200}

    engine = get_engine()
    # 默认值为 -1
    assert engine.pool._recycle == 7200  # type: ignore
    assert isinstance(engine.pool, NullPool)


@pytest.mark.parametrize(
    "app",
    [
        pytest.param(
            {"datastore_engine_options": {"poolclass": QueuePool}}, id="options"
        )
    ],
    indirect=True,
)
async def test_engine_options_poolclass(app: App):
    """测试设置引擎连接池"""
    from nonebot_plugin_datastore.db import get_engine

    engine = get_engine()
    assert isinstance(engine.pool, QueuePool)


@pytest.mark.parametrize(
    "app",
    [
        pytest.param(
            {"datastore_database_url": "sqlite+aiosqlite:///data/test/test.db"},
            id="url",
        )
    ],
    indirect=True,
)
async def test_create_db(app: App):
    """测试创建数据库"""
    from nonebot_plugin_datastore.db import init_db

    require("tests.example.plugin1")

    database_path = Path("data/test/test.db")

    assert not database_path.exists()
    await init_db()
    assert database_path.exists()

    database_path.unlink()
    database_path.parent.rmdir()
