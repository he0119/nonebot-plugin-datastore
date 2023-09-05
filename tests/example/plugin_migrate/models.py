from sqlalchemy.orm import Mapped, mapped_column

from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class Example(Model):
    """测试一下"""

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]
    test: Mapped[str]
