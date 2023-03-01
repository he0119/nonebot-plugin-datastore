from typing import Any

from sqlalchemy import JSON, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column

from .. import create_session, get_plugin_data
from . import ConfigProvider, KeyNotFoundError

plugin_data = get_plugin_data()


class ConfigModel(plugin_data.Model):
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)


class Config(ConfigProvider):
    """JSON 格式配置"""

    async def _get(self, key: str) -> Any:
        db_key = self._plugin_data.name + "_" + key
        try:
            async with create_session() as session:
                config = (
                    await session.scalars(
                        select(ConfigModel).where(ConfigModel.key == db_key)
                    )
                ).one()
                return config.value
        except NoResultFound:
            raise KeyNotFoundError(key)

    async def _set(self, key: str, value: Any) -> None:
        db_key = self._plugin_data.name + "_" + key
        async with create_session() as session:
            await session.merge(ConfigModel(key=db_key, value=value))
            await session.commit()

    def _get_sync(self, key: str) -> Any:
        raise NotImplementedError

    def _set_sync(self, key: str, value: Any) -> None:
        raise NotImplementedError
