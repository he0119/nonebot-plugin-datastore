from argparse import Namespace
from pathlib import Path
from typing import List, Optional

import click
from alembic import command
from alembic.config import Config as AlembicConfig
from nonebot import load_plugin
from nonebot.plugin import get_loaded_plugins

from nonebot_plugin_datastore import PluginData

PACKAGE_DIR = Path(__file__).parent


def get_plugins(name: Optional[str] = None) -> List[str]:
    """获取使用了数据库的插件名"""
    plugins = get_loaded_plugins()

    if name is None:
        return [
            plugin.name
            for plugin in plugins
            if plugin.module.__file__ and PluginData(plugin.name).metadata
        ]

    for plugin in plugins:
        if (
            name == plugin.name
            and plugin.module.__file__
            and PluginData(plugin.name).metadata
        ):
            return [plugin.name]

    # 如果插件没有在已加载的插件中找到，尝试加载插件
    plugin = load_plugin(name)
    if not plugin:
        click.echo(f"插件 {name} 不存在")
    elif plugin.module.__file__ and PluginData(plugin.name).metadata:
        return [plugin.name]
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
        click.echo(f"尝试生成 {plugin} 的迁移文件")
        config.set_main_option(
            "version_locations", str(PluginData(plugin).migration_dir)
        )
        config.set_main_option("plugin_name", plugin)
        command.revision(config, message, autogenerate=autogenerate)


def upgrade(name=None, revision="head"):
    """Upgrade to a later version."""
    config = Config()
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    plugins = get_plugins(name)
    for plugin in plugins:
        click.echo(f"升级 {plugin} 数据库")
        config.set_main_option(
            "version_locations", str(PluginData(plugin).migration_dir)
        )
        config.set_main_option("plugin_name", plugin)
        command.upgrade(config, revision)


def downgrade(name=None, revision="-1"):
    """Revert to a previous version."""
    config = Config()
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    plugins = get_plugins(name)
    for plugin in plugins:
        click.echo(f"降级 {plugin} 数据库")
        config.set_main_option(
            "version_locations", str(PluginData(plugin).migration_dir)
        )
        config.set_main_option("plugin_name", plugin)
        command.downgrade(config, revision)
