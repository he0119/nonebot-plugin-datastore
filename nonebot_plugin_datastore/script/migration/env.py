import asyncio

from alembic import context
from nonebot.log import logger
from sqlmodel import SQLModel

from nonebot_plugin_datastore import PluginData

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

plugin_name = config.get_main_option("plugin_name")

data = PluginData(plugin_name) if plugin_name else None
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = data.metadata if data else SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
version_table = f"{plugin_name}_alembic_version" if plugin_name else "alembic_version"


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.metadata.info.get("name") != plugin_name:
        return False
    else:
        return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        version_table=version_table,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    # 不生成空的迁移文件
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-empty-migrations-with-autogenerate
    def process_revision_directives(context, revision, directives):
        if config.cmd_opts and config.cmd_opts.autogenerate:
            script = directives[0]
            if script.upgrade_ops.is_empty():
                logger.info("没有检测到变更，跳过生成迁移文件")
                directives[:] = []

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table=version_table,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from nonebot_plugin_datastore.db import get_engine

    connectable = get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
