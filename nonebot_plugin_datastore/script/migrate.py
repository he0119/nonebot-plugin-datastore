from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config as AlembicConfig
from nonebot.plugin import get_loaded_plugins


def get_plugin_dir(name: Optional[str] = None) -> Optional[Path]:
    """通过插件名称获取插件目录"""
    plugins = get_loaded_plugins()
    for plugin in plugins:
        if name == plugin.name and plugin.module.__file__:
            package_dir = Path(plugin.module.__file__).parent
            return package_dir


class Config(AlembicConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
