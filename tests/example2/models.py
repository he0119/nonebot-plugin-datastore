from pathlib import Path
from typing import Optional

from sqlmodel import Field

from nonebot_plugin_datastore import PluginData

DATA = PluginData("example2")

DATA.set_migration_path(Path(__file__).parent / "test-migration")


class Example2(DATA.Model, table=True):
    """测试一下"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    message2: str
