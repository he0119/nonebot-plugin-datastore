import asyncio

import nonebot

from .db import init_db

if __name__ == "__main__":
    nonebot.load_plugin("nonebot_plugin_wordcloud")
    asyncio.run(init_db())
