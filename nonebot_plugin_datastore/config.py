"""配置"""

from pathlib import Path
from typing import Any

from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_cache_dir, get_config_dir, get_data_dir
from pydantic import BaseModel

from .compat import model_validator


class Config(BaseModel):
    datastore_cache_dir: Path
    datastore_config_dir: Path
    datastore_data_dir: Path
    datastore_database_url: str
    """数据库连接字符串

    默认使用 SQLite
    """
    datastore_enable_database: bool = True
    datastore_database_echo: bool = False
    datastore_engine_options: dict[str, Any] = {}
    datastore_config_provider: str = "~json"

    @model_validator(mode="before")
    def set_defaults(cls, values: dict):
        """设置默认值"""
        # 设置默认目录
        # 仅在未设置时调用 get_*_dir 函数，因为这些函数会自动创建目录
        values["datastore_cache_dir"] = (
            Path(cache_dir)
            if (cache_dir := values.get("datastore_cache_dir"))
            else Path(get_cache_dir(""))
        )
        values["datastore_config_dir"] = (
            Path(config_dir)
            if (config_dir := values.get("datastore_config_dir"))
            else Path(get_config_dir(""))
        )
        values["datastore_data_dir"] = (
            Path(data_dir)
            if (data_dir := values.get("datastore_data_dir"))
            else Path(get_data_dir(""))
        )

        # 设置默认数据库连接字符串
        if not values.get("datastore_database_url"):
            values["datastore_database_url"] = (
                f"sqlite+aiosqlite:///{values['datastore_data_dir'] / 'data.db'}"
            )

        return values


plugin_config = get_plugin_config(Config)
