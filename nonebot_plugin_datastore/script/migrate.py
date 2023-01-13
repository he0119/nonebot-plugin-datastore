from argparse import Namespace
from pathlib import Path
from typing import List, Optional, TypedDict

import click
from alembic import command
from alembic.config import Config as AlembicConfig
from nonebot.plugin import get_loaded_plugins

from nonebot_plugin_datastore import PluginData

PACKAGE_DIR = Path(__file__).parent


class PluginInfo(TypedDict):
    name: str
    path: Path


def get_plugins(name: Optional[str] = None) -> List[PluginInfo]:
    """通过插件名称获取插件目录"""
    plugins = get_loaded_plugins()

    if name is None:
        return [
            PluginInfo(name=plugin.name, path=Path(plugin.module.__file__).parent)
            for plugin in plugins
            if plugin.module.__file__ and PluginData(plugin.name).metadata
        ]

    for plugin in plugins:
        if (
            name == plugin.name
            and plugin.module.__file__
            and PluginData(plugin.name).metadata
        ):
            package_dir = Path(plugin.module.__file__).parent
            return [PluginInfo(name=plugin.name, path=package_dir)]
    return []


class Config(AlembicConfig):
    def __init__(self, *args, **kwargs):
        self.template_directory = kwargs.pop("template_directory", None)
        super().__init__(*args, **kwargs)

    def get_template_directory(self):
        if self.template_directory:
            return self.template_directory
        package_dir = Path(__file__).parent
        return str(package_dir / "migration")


def revision(name=None, message=None, autogenerate=False):
    """Create a new revision file."""
    config = Config(cmd_opts=Namespace(autogenerate=autogenerate))
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    plugins = get_plugins(name)
    for plugin in plugins:
        click.echo(f"尝试生成 {plugin['name']} 的迁移文件")
        config.set_main_option("version_locations", str(plugin["path"] / "versions"))
        config.set_main_option("plugin_name", plugin["name"])
        command.revision(config, message, autogenerate=autogenerate)


def upgrade(name=None, revision="head"):
    """Upgrade to a later version."""
    config = Config()
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    plugins = get_plugins(name)
    for plugin in plugins:
        click.echo(f"升级 {plugin['name']} 的数据库")
        config.set_main_option("version_locations", str(plugin["path"] / "versions"))
        config.set_main_option("plugin_name", plugin["name"])
        command.upgrade(config, revision)
