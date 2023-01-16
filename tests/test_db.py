from typing import List, Optional, cast

import pytest
from nonebug import App

from .utils import make_fake_event, make_fake_message


async def test_db(app: App):
    """测试数据库"""
    from nonebot import require
    from sqlmodel import select

    from nonebot_plugin_datastore.db import create_session, init_db

    require("tests.example")
    from .example import Example, test

    await init_db()

    async with create_session() as session:
        statement = select(Example)
        result = await session.exec(statement)  # type: ignore
        example = cast(Example, result.first())
        assert example.message == "post"

    async with create_session() as session:
        session.add(Example(message="test"))
        await session.commit()

    async with create_session() as session:
        statement = select(Example)
        examples: List[Example] = (await session.exec(statement)).all()  # type: ignore
        assert len(examples) == 2
        assert examples[1].message == "test"

    message = make_fake_message()("/test")
    event = make_fake_event(_message=message)()

    async with app.test_matcher(test) as ctx:
        bot = ctx.create_bot()

        ctx.receive_event(bot, event)

    async with create_session() as session:
        statement = select(Example)
        examples: List[Example] = (await session.exec(statement)).all()  # type: ignore
        assert len(examples) == 3
        assert examples[2].message == "matcher"


@pytest.mark.parametrize(
    "nonebug_init",
    [pytest.param({"datastore_enable_database": "false"}, id="disable_db")],
    indirect=True,
)
async def test_disable_db(app: App):
    """测试禁用数据库"""
    from nonebot_plugin_datastore import create_session

    with pytest.raises(ValueError) as e:
        async with create_session() as session:
            pass

    assert str(e.value) == "数据库未启用"


async def test_default_db_url(nonebug_init: None):
    """测试默认数据库地址"""
    import nonebot

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_datastore")

    from nonebot_plugin_datastore.config import BASE_DATA_DIR, plugin_config

    assert (
        plugin_config.datastore_database_url
        == f"sqlite+aiosqlite:///{BASE_DATA_DIR / 'data.db'}"
    )


async def test_post_db_init_error(app: None):
    """数据库初始化后执行函数错误"""
    from nonebot_plugin_datastore.db import init_db, post_db_init

    @post_db_init
    async def _():
        raise Exception("test")

    await init_db()


async def test_pre_db_init_error(app: None):
    """数据库初始化前执行函数错误"""
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db

    require("tests.example2")

    await init_db()


async def test_compatibility(app: None):
    """测试兼容不使用迁移的旧版本，且新旧版本共存"""
    from nonebot import require
    from sqlmodel import Field, SQLModel, select

    from nonebot_plugin_datastore.db import create_session, init_db

    require("tests.example")
    from .example import Example

    class Test(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        message: str

    await init_db()

    async with create_session() as session:
        session.add(Test(message="test"))
        await session.commit()

    async with create_session() as session:
        statement = select(Example)
        result = await session.exec(statement)  # type: ignore
        example = cast(Example, result.first())
        assert example.message == "post"
