from pathlib import Path
from typing import List

import nonebot
import pytest
from nonebug import App

from .utils import make_fake_event, make_fake_message


@pytest.mark.asyncio
async def test_db(app: App):
    """测试数据库"""
    from sqlmodel import select

    from nonebot_plugin_datastore.db import create_session, init_db

    from .example import Example, test

    nonebot.load_plugin("tests.example")

    await init_db()

    async with create_session() as session:
        session.add(Example(message="test"))
        await session.commit()

    async with create_session() as session:
        statement = select(Example)
        examples: List[Example] = (await session.exec(statement)).all()  # type: ignore
        assert len(examples) == 1
        assert examples[0].message == "test"

    message = make_fake_message()("/test")
    event = make_fake_event(_message=message)()

    async with app.test_matcher(test) as ctx:
        bot = ctx.create_bot()

        ctx.receive_event(bot, event)

    async with create_session() as session:
        statement = select(Example)
        examples: List[Example] = (await session.exec(statement)).all()  # type: ignore
        assert len(examples) == 2
        assert examples[1].message == "matcher"


@pytest.mark.asyncio
async def test_disable_db(nonebug_init: None, tmp_path: Path):
    """测试禁用数据库"""
    import nonebot

    config = nonebot.get_driver().config
    # 插件数据目录
    config.datastore_cache_dir = tmp_path / "cache"
    config.datastore_config_dir = tmp_path / "config"
    config.datastore_data_dir = tmp_path / "data"

    # 禁用数据库
    config.datastore_enable_database = False

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_datastore")

    from nonebot_plugin_datastore import create_session

    with pytest.raises(ValueError) as e:
        async with create_session() as session:
            pass

    assert str(e.value) == "数据库未启用"


@pytest.mark.asyncio
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
