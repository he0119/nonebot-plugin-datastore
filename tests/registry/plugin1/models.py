from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class Example(Model):
    """测试一下"""

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]

    tests: Mapped["Test"] = relationship(back_populates="example")


class Test(Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    example_id: Mapped[int] = mapped_column(ForeignKey("plugin1_example.id"))
    example: Mapped[Example] = relationship(back_populates="tests")
