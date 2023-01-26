from argparse import Namespace
from typing import Optional

import anyio
import click
from nb_cli.cli import run_async, run_sync
from nonebot.log import logger

from ..config import plugin_config
from ..plugin import PluginData
from . import command
from .utils import Config, get_plugins


@click.group()
def cli():
    """Datastore CLI"""
    pass


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=(
        "Populate revision script with candidate migration "
        "operations, based on comparison of database to model"
    ),
)
@run_async
async def revision(name: Optional[str], message: Optional[str], autogenerate: bool):
    """创建迁移文件"""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"尝试生成插件 {plugin} 的迁移文件")
        config = Config(plugin, cmd_opts=Namespace(autogenerate=autogenerate))
        await command.revision(config, message, autogenerate=autogenerate)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("-m", "--message", default=None, help="Revision message")
@run_async
async def migrate(name: Optional[str], message: Optional[str]):
    """自动根据模型更改创建迁移文件"""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"尝试生成插件 {plugin} 的迁移文件")
        config = Config(plugin, cmd_opts=Namespace(autogenerate=True))
        await command.revision(config, message, autogenerate=True)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.argument("revision", default="head")
@run_async
async def upgrade(name: Optional[str], revision: str):
    """升级数据库版本"""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"升级插件 {plugin} 的数据库")
        config = Config(plugin)
        await command.upgrade(config, revision)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.argument("revision", default="-1")
@run_async
async def downgrade(name: Optional[str], revision: str):
    """降级数据库版本"""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"降级插件 {plugin} 的数据库")
        config = Config(plugin)
        await command.downgrade(config, revision)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--rev-range", "-r", default=None, help="Revision range")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option(
    "--indicate-current",
    "-i",
    is_flag=True,
    help="Indicate current revisions with (head) and (current)",
)
@run_async
async def history(
    name: Optional[str],
    rev_range: Optional[str],
    verbose: bool,
    indicate_current: bool,
):
    """数据库版本历史"""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库历史")
        config = Config(plugin)
        await command.history(config, rev_range, verbose, indicate_current)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@run_async
async def current(name: Optional[str], verbose: bool):
    """数据库当前版本"""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库当前版本")
        config = Config(plugin)
        await command.current(config, verbose)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def heads(name: Optional[str], verbose: bool):
    """数据库最新版本"""
    plugins = get_plugins(name)
    for plugin in plugins:
        logger.info(f"查看插件 {plugin} 的数据库当前可用的 heads")
        config = Config(plugin)
        command.heads(config, verbose)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@run_async
async def check(name: Optional[str]):
    """数据库是否需要升级"""
    plugins = get_plugins(name, True)
    for plugin in plugins:
        logger.info(f"检查插件 {plugin} 的数据库是否需要新的迁移文件")
        config = Config(plugin)
        await command.check(config)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
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


def main():
    anyio.run(run_sync(cli))  # pragma: no cover
