from nonebot import on_command
from nonebot.params import Depends

from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import AsyncSession

from .models import Example2

test = on_command("test")


@test.handle()
async def test_handle(session: AsyncSession = Depends(get_session)):
    example = Example2(message2="matcher")
    session.add(example)
    await session.commit()
