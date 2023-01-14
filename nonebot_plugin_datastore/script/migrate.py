from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from alembic import command
from alembic.config import Config as AlembicConfig
from nonebot import load_plugin
from nonebot.log import logger
from nonebot.plugin import get_loaded_plugins

from nonebot_plugin_datastore import PluginData

if TYPE_CHECKING:
    from nonebot.plugin import Plugin

PACKAGE_DIR = Path(__file__).parent
SCRIPT_LOCATION = PACKAGE_DIR / "migration"


def get_plugins(name: Optional[str] = None, exclude_others: bool = False) -> List[str]:
    """获取使用了数据库的插件名"""

    def _should_include(plugin: "Plugin") -> bool:
        # 使用了数据库
        if not PluginData(plugin.name).metadata:
            return False

        # 有文件
        if not plugin.module.__file__:
            return False

        # 是否排除当前项目外的插件
        if exclude_others:
            # 排除 site-packages 中的插件
            if "site-packages" in plugin.module.__file__:
                return False
            # 在当前项目目录中
            if Path.cwd() not in Path(plugin.module.__file__).parents:
                return False

        return True

    plugins = get_loaded_plugins()

    if name is None:
        return [plugin.name for plugin in plugins if _should_include(plugin)]

    for plugin in plugins:
        if name == plugin.name and _should_include(plugin):
            return [plugin.name]

    return []


class Config(AlembicConfig):
    def __init__(self, plugin_name, *args, **kwargs):
        self.template_directory = kwargs.pop("template_directory", None)
        super().__init__(*args, **kwargs)
        self.set_main_option("script_location", str(SCRIPT_LOCATION))
        self.set_main_option("plugin_name", plugin_name)
        self.set_main_option(
            "version_locations", str(PluginData(plugin_name).migration_dir)
        )

    def get_template_directory(self):
        if self.template_directory:
            return self.template_directory
        return str(SCRIPT_LOCATION)


def revision(name=None, message=None, autogenerate=False):
    """Create a new revision file."""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"尝试生成插件 {plugin} 的迁移文件")
        config = Config(plugin, cmd_opts=Namespace(autogenerate=autogenerate))
        command.revision(config, message, autogenerate=autogenerate)


def upgrade(name=None, revision="head"):
    """Upgrade to a later version."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"升级插件 {plugin} 的数据库")
        config = Config(plugin)
        command.upgrade(config, revision)


def downgrade(name=None, revision="-1"):
    """Revert to a previous version."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"降级插件 {plugin} 的数据库")
        config = Config(plugin)
        command.downgrade(config, revision)
