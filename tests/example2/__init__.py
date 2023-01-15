from nonebot import on_command
from nonebot.params import Depends

from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import AsyncSession, create_session, pre_db_init

from .models import Example2


@pre_db_init
async def _():
    async with create_session() as session:
        example = Example2(message2="pre")
        session.add(example)
        await session.commit()


test2 = on_command("test2")


@test2.handle()
async def test_handle(session: AsyncSession = Depends(get_session)):
    example = Example2(message2="matcher")
    session.add(example)
    await session.commit()
