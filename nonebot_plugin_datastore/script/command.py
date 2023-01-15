from argparse import Namespace

from alembic import command
from nonebot.log import logger

from .utils import Config, get_plugins


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
