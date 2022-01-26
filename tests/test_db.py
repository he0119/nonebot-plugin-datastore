import nonebot
import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_db(app: App):
    """测试数据库"""
    from sqlmodel import select

    from nonebot_plugin_datastore.db import create_session, init_db

    from .example import Example

    nonebot.load_plugin("tests.example")

    await init_db()

    async with create_session() as session:
        session.add(Example(message="test"))
        await session.commit()

    async with create_session() as session:
        statement = select(Example)
        example: Example = (await session.exec(statement)).first()  # type: ignore
        assert example.message == "test"
