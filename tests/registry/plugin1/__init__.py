from nonebot import on_command
from nonebot.params import Depends

from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import AsyncSession

from .models import Example, Test

test = on_command("test")


@test.handle()
async def _(session: AsyncSession = Depends(get_session)):
    session.add(Example(message="matcher"))
    await session.commit()
