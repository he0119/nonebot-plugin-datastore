from alembic import context
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from nonebot.log import logger

from nonebot_plugin_datastore.db import get_engine
from nonebot_plugin_datastore.plugin import PluginData
from nonebot_plugin_datastore.script.migrate import Config, get_plugins


def do_run_migrations(connection, plugin_name: str, autogenerate: bool):
    target_metadata = PluginData(plugin_name).metadata

    # 不生成空的迁移文件
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-empty-migrations-with-autogenerate
    def process_revision_directives(context, revision, directives):
        if autogenerate:
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
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migration(plugin_name: str, autogenerate: bool = False):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations, plugin_name, autogenerate)


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
