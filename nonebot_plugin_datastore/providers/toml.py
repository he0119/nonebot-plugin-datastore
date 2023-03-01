from pathlib import Path
from typing import TYPE_CHECKING, Any

import rtoml

from . import ConfigProvider, KeyNotFoundError

if TYPE_CHECKING:
    from ..plugin import PluginData


class Config(ConfigProvider):
    """toml 格式配置"""

    def __init__(self, plugin_data: "PluginData") -> None:
        super().__init__(plugin_data)
        self._data = {}
        self._load_config()

    @property
    def _path(self) -> Path:
        """配置文件路径"""
        return self._plugin_data.config_dir / f"{self._plugin_data.name}.toml"

    def _ensure_config(self) -> None:
        """确保配置文件存在"""
        if not self._path.exists():
            with self._path.open("w", encoding="utf8") as f:
                rtoml.dump(self._data, f)

    def _load_config(self) -> None:
        """读取配置"""
        self._ensure_config()
        with self._path.open("r", encoding="utf8") as f:
            self._data = rtoml.load(f)

    def _save_config(self) -> None:
        """保存配置"""
        self._ensure_config()
        with self._path.open("w", encoding="utf8") as f:
            rtoml.dump(self._data, f)

    async def _get(self, key: str) -> Any:
        if not self._data:
            self._load_config()
        try:
            return self._data[key]
        except KeyError:
            raise KeyNotFoundError(key)

    async def _set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save_config()
