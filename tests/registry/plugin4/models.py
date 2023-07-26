from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nonebot_plugin_datastore import get_plugin_data
from tests.registry.plugin3.models import Example

db = get_plugin_data()
db.use_global_registry()

Model = db.Model


class Test(Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    example_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plugin3_example.id"))
    example: Mapped[Optional[Example]] = relationship(Example, back_populates="tests4")


Example.tests4 = relationship(Test, back_populates="example")
