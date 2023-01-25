from argparse import Namespace
from typing import Optional

import click
from alembic import command
from nonebot.log import logger

from ..config import plugin_config
from ..plugin import PluginData
from .utils import Config, get_plugins


def revision(
    name: Optional[str] = None,
    message: Optional[str] = None,
    autogenerate: bool = False,
):
    """Create a new revision file."""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"尝试生成插件 {plugin} 的迁移文件")
        config = Config(plugin, cmd_opts=Namespace(autogenerate=autogenerate))
        command.revision(config, message, autogenerate=autogenerate)


def upgrade(name: Optional[str] = None, revision: str = "head"):
    """Upgrade to a later version."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"升级插件 {plugin} 的数据库")
        config = Config(plugin)
        command.upgrade(config, revision)


def downgrade(name: Optional[str] = None, revision: str = "-1"):
    """Revert to a previous version."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"降级插件 {plugin} 的数据库")
        config = Config(plugin)
        command.downgrade(config, revision)


def history(
    name: Optional[str] = None,
    rev_range: Optional[str] = None,
    verbose: bool = False,
    indicate_current: bool = False,
):
    """List changeset scripts in chronological order."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库历史")
        config = Config(plugin)
        command.history(config, rev_range, verbose, indicate_current)


def current(name: Optional[str] = None, verbose: bool = False):
    """Display the current revision for a database."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库当前版本")
        config = Config(plugin)
        command.current(config, verbose)


def heads(name: Optional[str] = None, verbose: bool = False):
    """Show current available heads in the script directory."""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库当前可用的 heads")
        config = Config(plugin)
        command.heads(config, verbose)


def check(name: Optional[str] = None):
    """Check if revision command with autogenerate has pending upgrade ops."""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"检查插件 {plugin} 的数据库是否需要新的迁移文件")
        config = Config(plugin)
        command.check(config)


def dir(name: Optional[str] = None):
    """数据存储路径"""
    if name is None:
        click.echo("当前存储路径:")
        click.echo(f"缓存目录: {plugin_config.datastore_cache_dir}")
        click.echo(f"配置目录: {plugin_config.datastore_config_dir}")
        click.echo(f"数据目录: {plugin_config.datastore_data_dir}")
        return

    plugins = get_plugins(name)
    for plugin in plugins:
        plugin_data = PluginData(plugin)
        click.echo(f"插件 {plugin} 的存储路径:")
        click.echo(f"缓存目录: {plugin_data.cache_dir}")
        click.echo(f"配置目录: {plugin_data.config_dir}")
        click.echo(f"数据目录: {plugin_data.data_dir}")
