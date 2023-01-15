from nonebot import on_command
from nonebot.params import Depends

from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import AsyncSession, create_session, post_db_init

from .models import Example


@post_db_init
async def _():
    async with create_session() as session:
        example = Example(message="init")
        session.add(example)
        await session.commit()


test = on_command("test")


@test.handle()
async def test_handle(session: AsyncSession = Depends(get_session)):
    example = Example(message="matcher")
    session.add(example)
    await session.commit()
