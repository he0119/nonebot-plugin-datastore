from typing import List, Optional, cast

import pytest
from nonebot import require
from nonebug import App

from .utils import make_fake_event, make_fake_message


async def test_db(app: App):
    """测试数据库"""
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


async def test_default_db_url(app: App):
    """测试默认数据库地址"""
    from nonebot_plugin_datastore.config import plugin_config

    assert (
        plugin_config.datastore_database_url
        == f"sqlite+aiosqlite:///{plugin_config.datastore_data_dir / 'data.db'}"
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
    from nonebot_plugin_datastore.db import init_db

    require("tests.example2")

    with pytest.raises(Exception):
        await init_db()


async def test_compatibility(app: None):
    """测试兼容不使用迁移的旧版本，且新旧版本共存"""
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
