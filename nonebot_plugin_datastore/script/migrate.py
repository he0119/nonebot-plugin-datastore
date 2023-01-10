from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config as AlembicConfig
from nonebot.plugin import get_loaded_plugins

PACKAGE_DIR = Path(__file__).parent


def get_plugin_dir(name: Optional[str] = None) -> Optional[Path]:
    """通过插件名称获取插件目录"""
    plugins = get_loaded_plugins()
    for plugin in plugins:
        if name == plugin.name and plugin.module.__file__:
            package_dir = Path(plugin.module.__file__).parent
            return package_dir


class Config(AlembicConfig):
    def __init__(self, *args, **kwargs):
        self.template_directory = kwargs.pop("template_directory", None)
        super().__init__(*args, **kwargs)

    def get_template_directory(self):
        if self.template_directory:
            return self.template_directory
        package_dir = Path(__file__).parent
        return str(package_dir / "migration")


def revision(
    message=None,
    autogenerate=False,
    sql=False,
    head="head",
    splice=False,
    branch_label=None,
    version_path=None,
    rev_id=None,
):
    """Create a new revision file."""
    config = Config()
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    directory = get_plugin_dir("example")
    if directory:
        config.set_main_option("version_locations", str(directory / "versions"))
        command.revision(
            config,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id,
        )


def upgrade(revision="head", sql=False, tag=None):
    """Upgrade to a later version."""
    config = Config()
    config.set_main_option("script_location", str(PACKAGE_DIR / "migration"))
    directory = get_plugin_dir("example")
    if directory:
        config.set_main_option("version_locations", str(directory / "versions"))
        command.upgrade(config, revision, sql=sql, tag=tag)
