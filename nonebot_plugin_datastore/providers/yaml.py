from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from . import ConfigProvider, KeyNotFoundError

if TYPE_CHECKING:
    from ..plugin import PluginData


class Config(ConfigProvider):
    """yaml 格式配置"""

    def __init__(self, plugin_data: "PluginData") -> None:
        super().__init__(plugin_data)
        self._data = {}
        self._load_config()

    @property
    def _path(self) -> Path:
        """配置文件路径"""
        return self._plugin_data.config_dir / f"{self._plugin_data.name}.yaml"

    def _ensure_config(self) -> None:
        """确保配置文件存在"""
        if not self._path.exists():
            with self._path.open("w", encoding="utf8") as f:
                yaml.dump(self._data, f, Dumper=Dumper)

    def _load_config(self) -> None:
        """读取配置"""
        self._ensure_config()
        with self._path.open("r", encoding="utf8") as f:
            self._data = yaml.load(f, Loader=Loader)

    def _save_config(self) -> None:
        """保存配置"""
        self._ensure_config()
        with self._path.open("w", encoding="utf8") as f:
            yaml.dump(self._data, f, Dumper=Dumper)

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
