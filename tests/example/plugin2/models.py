from pathlib import Path

from sqlalchemy.orm import Mapped, mapped_column

from nonebot_plugin_datastore import get_plugin_data

DATA = get_plugin_data("plugin2")

DATA.set_migration_dir(Path(__file__).parent / "test-migration")


class Example2(DATA.Model):
    """测试一下"""

    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]
