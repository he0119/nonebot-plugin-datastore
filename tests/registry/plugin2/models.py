from typing import List, Optional

from sqlmodel import Field, Relationship

from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class Example(Model, table=True):
    """测试一下"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    message: str

    tests: List["Test"] = Relationship(back_populates="example")


class Test(Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    example_id: Optional[int] = Field(default=None, foreign_key="plugin2_example.id")
    example: Optional[Example] = Relationship(back_populates="tests")
