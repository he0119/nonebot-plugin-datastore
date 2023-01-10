from typing import Optional

from sqlmodel import Field, SQLModel


class Example(SQLModel, table=True):
    """测试一下"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
