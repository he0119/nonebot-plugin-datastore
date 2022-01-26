from typing import Optional

from sqlmodel import Field, SQLModel


class Example(SQLModel, table=True):
    """测试一下"""

    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
