import nonebot

# 检查 NoneBot 是否初始化
# 如果没有初始化，说明是在命令行中运行
try:
    nonebot.get_driver()
except ValueError:
    # 初始化
    # 使用内存数据库，因为每次运行都需要是新数据库
    nonebot.init(
        datastore_database_url="sqlite+aiosqlite:///:memory:",
        datastore_database_echo=True,
    )

from nonebot.plugin import export

from .db import create_session as create_session
from .db import get_session as get_session
from .plugin import PluginData as PluginData

export.get_session = get_session
export.create_session = create_session
export.PluginData = PluginData
