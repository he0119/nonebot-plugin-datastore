from alembic import context
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from nonebot.log import logger

from nonebot_plugin_datastore.db import get_engine
from nonebot_plugin_datastore.plugin import PluginData
from nonebot_plugin_datastore.script.migrate import Config, get_plugins


def do_run_migrations(connection, plugin_name: str):
    target_metadata = PluginData(plugin_name).metadata

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
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migration(plugin_name: str):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations, plugin_name)


async def run_upgrade():
    """初始化数据库"""
    plugins = get_plugins()
    for plugin in plugins:
        logger.info(f"初始化插件 {plugin} 的数据库")
        config = Config()
        config.set_main_option(
            "version_locations", str(PluginData(plugin).migration_dir)
        )
        script = ScriptDirectory.from_config(config)

        def upgrade(rev, context):
            return script._upgrade_revs("head", rev)

        with EnvironmentContext(config, script, fn=upgrade):
            await run_migration(plugin)
