from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from alembic import context
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from click import BadParameter
from nonebot import get_loaded_plugins, get_plugin
from nonebot.log import logger

from nonebot_plugin_datastore import PluginData
from nonebot_plugin_datastore.db import get_engine

if TYPE_CHECKING:
    from nonebot.plugin import Plugin

SCRIPT_LOCATION = Path(__file__).parent / "migration"


def get_plugins(name: Optional[str] = None, exclude_others: bool = False) -> List[str]:
    """获取使用了数据库的插件名"""

    def _should_include(plugin: "Plugin") -> bool:
        # 使用了数据库
        if not PluginData(plugin.name).metadata:
            return False

        # 有文件
        if not plugin.module.__file__:
            return False  # pragma: no cover

        # 是否排除当前项目外的插件
        if exclude_others:
            # 排除 site-packages 中的插件
            if "site-packages" in plugin.module.__file__:
                return False  # pragma: no cover
            # 在当前项目目录中
            if Path.cwd() not in Path(plugin.module.__file__).parents:
                return False

        return True

    if name is None:
        return [
            plugin.name for plugin in get_loaded_plugins() if _should_include(plugin)
        ]

    if (plugin := get_plugin(name)) and _should_include(plugin):
        return [plugin.name]

    raise BadParameter(message="未找到插件", param_hint="name")


class Config(AlembicConfig):
    def __init__(self, plugin_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_main_option("plugin_name", plugin_name)
        self.set_main_option("script_location", str(SCRIPT_LOCATION))
        self.set_main_option(
            "version_locations", str(PluginData(plugin_name).migration_dir)
        )


def do_run_migrations(connection, plugin_name: Optional[str] = None):
    config = context.config

    if plugin_name is None:
        plugin_name = config.get_main_option("plugin_name")

    if not plugin_name:
        raise ValueError("未指定插件名称")  # pragma: no cover

    target_metadata = PluginData(plugin_name).metadata

    # 不生成空的迁移文件
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-empty-migrations-with-autogenerate
    def process_revision_directives(context, revision, directives):
        if config.cmd_opts and config.cmd_opts.autogenerate:
            script = directives[0]
            if script.upgrade_ops.is_empty():
                logger.info("模型未发生变化，已跳过生成迁移文件")
                directives[:] = []

    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table" and object.metadata.info.get("name") != plugin_name:
            return False
        else:
            return True

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table=f"{plugin_name}_alembic_version",
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        render_as_batch=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migration(plugin_name: Optional[str] = None):
    """运行迁移"""
    connectable = get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations, plugin_name)


async def run_upgrade():
    """初始化数据库"""
    plugins = get_plugins()
    for plugin in plugins:
        logger.debug(f"初始化插件 {plugin} 的数据库")

        config = Config(plugin)
        script = ScriptDirectory.from_config(config)

        def upgrade(rev, context):
            return script._upgrade_revs("head", rev)

        with EnvironmentContext(config, script, fn=upgrade):
            await run_migration(plugin)
