from pathlib import Path
from typing import Optional

from sqlmodel import Field

from nonebot_plugin_datastore import get_plugin_data

DATA = get_plugin_data("plugin2")

DATA.set_migration_dir(Path(__file__).parent / "test-migration")


class Example2(DATA.Model, table=True):
    """测试一下"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    message2: str
