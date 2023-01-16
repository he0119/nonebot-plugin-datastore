""" 配置 """
from pathlib import Path
from typing import Dict

from nonebot import get_driver, require
from pydantic import BaseModel, Extra, root_validator

require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_cache_dir, get_config_dir, get_data_dir

# 默认目录
BASE_CACHE_DIR: Path = Path(get_cache_dir(""))
BASE_CONFIG_DIR: Path = Path(get_config_dir(""))
BASE_DATA_DIR: Path = Path(get_data_dir(""))


class Config(BaseModel, extra=Extra.ignore):
    datastore_cache_dir: Path = BASE_CACHE_DIR
    datastore_config_dir: Path = BASE_CONFIG_DIR
    datastore_data_dir: Path = BASE_DATA_DIR
    datastore_enable_database: bool = True
    datastore_database_url: str
    """数据库连接字符串

    默认使用 SQLite
    """
    datastore_database_echo: bool = False

    @root_validator(pre=True, allow_reuse=True)
    def set_database_url(cls, values: Dict):
        database_url = values.get("datastore_database_url")
        data_dir = values.get("datastore_data_dir")
        if database_url is None:
            if data_dir is None:
                data_dir = BASE_DATA_DIR
            else:
                data_dir = Path(data_dir)
            values[
                "datastore_database_url"
            ] = f"sqlite+aiosqlite:///{data_dir / 'data.db'}"
        return values


plugin_config = Config.parse_obj(get_driver().config)
