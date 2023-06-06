from nonebot import require

require("nonebot_plugin_localstore")

from nonebot.plugin import PluginMetadata

from .config import Config
from .db import create_session as create_session
from .db import get_session as get_session
from .plugin import PluginData as PluginData
from .plugin import get_plugin_data as get_plugin_data

__plugin_meta__ = PluginMetadata(
    name="数据存储",
    description="NoneBot 数据存储插件",
    usage="请参考文档",
    type="library",
    homepage="https://github.com/he0119/nonebot-plugin-datastore",
    config=Config,
)
