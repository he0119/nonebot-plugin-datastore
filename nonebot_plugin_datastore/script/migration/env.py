import asyncio

from alembic import context

from nonebot_plugin_datastore.script.migration.utils import run_migration

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

plugin_name = config.get_main_option("plugin_name")

if not plugin_name:
    raise RuntimeError("未指定插件名称")  # pragma: no cover

if config.cmd_opts and config.cmd_opts.autogenerate:
    autogenerate = True
else:
    autogenerate = False

if not context.is_offline_mode():
    asyncio.run(run_migration(plugin_name, autogenerate))
