""" 插件数据 """
import abc
import json
import pickle
from pathlib import Path
from typing import IO, Any, Callable, Generic, Optional, Type, TypeVar, Union, overload

import httpx
from nonebot import get_plugin
from nonebot.log import logger
from sqlalchemy.orm import declared_attr, registry
from sqlmodel import MetaData, SQLModel

from .config import plugin_config
from .utils import get_caller_plugin_name

T = TypeVar("T")
R = TypeVar("R")


class Config(abc.ABC):
    """插件配置管理"""

    def __init__(self, plugin_data: "PluginData") -> None:
        self._plugin_data = plugin_data

    @abc.abstractmethod
    def _get(self, key: str) -> Any:
        """获取配置键值"""
        # TODO: 支持从数据库读取数据
        raise NotImplementedError

    @abc.abstractmethod
    def _set(self, key: str, value: Any) -> None:
        """设置配置键值"""
        raise NotImplementedError

    @overload
    def get(self, __key: str) -> Union[Any, None]:
        ...

    @overload
    def get(self, __key: str, __default: T) -> T:
        ...

    def get(self, key, default=None):
        """获得配置

        如果配置获取失败则使用 `default` 值并保存
        如果不提供 `default` 默认返回 None
        """
        try:
            value = self._get(key)
        except:
            value = default
            # 保存默认配置
            self.set(key, value)
        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置"""
        self._set(key, value)


class JsonConfig(Config):
    """JSON 格式配置"""

    def __init__(self, plugin_data: "PluginData") -> None:
        super().__init__(plugin_data)
        self._data = {}
        self._load_config()

    @property
    def _path(self) -> Path:
        """配置文件路径"""
        return self._plugin_data.config_dir / f"{self._plugin_data.name}.json"

    def _ensure_config(self) -> None:
        """确保配置文件存在"""
        if not self._path.exists():
            with self._path.open("w", encoding="utf8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> None:
        """读取配置"""
        self._ensure_config()
        with self._path.open("r", encoding="utf8") as f:
            self._data = json.load(f)

    def _save_config(self) -> None:
        """保存配置"""
        self._ensure_config()
        with self._path.open("w", encoding="utf8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _get(self, key: str) -> Any:
        if not self._data:
            self._load_config()
        return self._data[key]

    def _set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save_config()


class NetworkFile(Generic[T, R]):
    """从网络获取文件

    暂时只支持 json 格式
    """

    def __init__(
        self,
        url: str,
        filename: str,
        plugin_data: "PluginData",
        process_data: Optional[Callable[[T], R]] = None,
        cache: bool = False,
    ) -> None:
        self._url = url
        self._filename = filename
        self._plugin_data = plugin_data
        self._process_data = process_data
        self._cache = cache

        self._data: Optional[R] = None

    async def load_from_network(self) -> T:
        """从网络加载文件"""
        logger.info("正在从网络获取数据")
        content = await self._plugin_data.download_file(
            self._url, self._filename, self._cache
        )
        rjson = json.loads(content)
        return rjson

    def load_from_local(self) -> T:
        """从本地获取数据"""
        logger.info("正在加载本地数据")
        data = self._plugin_data.load_json(self._filename)
        return data

    @property
    async def data(self) -> R:
        """数据

        先从本地加载，如果本地文件不存在则从网络加载
        """
        if self._data is None:
            if self._plugin_data.exists(self._filename):
                data = self.load_from_local()
            else:
                data = await self.load_from_network()
            # 处理数据
            if self._process_data:
                self._data = self._process_data(data)
            else:
                self._data = data  # type: ignore
        return self._data  # type: ignore

    async def update(self) -> None:
        """从网络更新数据"""
        self._data = await self.load_from_network()  # type: ignore
        if self._process_data:
            self._data = self._process_data(self._data)


class Singleton(type):
    """单例

    每个相同名称的插件数据只需要一个实例
    """

    _instances = {}

    def __call__(cls, name: str):
        if not cls._instances.get(name):
            cls._instances[name] = super().__call__(name)
        return cls._instances[name]


class PluginData(metaclass=Singleton):
    """插件数据管理

    将插件数据保存在 `data` 文件夹对应的目录下。
    提供保存和读取文件/数据的方法。
    """

    def __init__(self, name: str) -> None:
        # 插件名，用来确定插件的文件夹位置
        self.name = name

        # 插件配置
        self._config = None

        # 数据库
        self._metadata = None
        self._model = None
        self._migration_path = None

    @staticmethod
    def _ensure_dir(path: Path):
        """确保目录存在"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise RuntimeError(f"{path} 不是目录")

    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        directory = plugin_config.datastore_cache_dir / self.name
        # 每次调用都检查一下目录是否存在
        # 防止运行时有人删除目录
        self._ensure_dir(directory)
        return directory

    @property
    def config_dir(self) -> Path:
        """配置目录

        配置都放置在统一的目录下
        """
        directory = plugin_config.datastore_config_dir
        self._ensure_dir(directory)
        return directory

    @property
    def data_dir(self) -> Path:
        """数据目录"""
        directory = plugin_config.datastore_data_dir / self.name
        self._ensure_dir(directory)
        return directory

    @property
    def config(self) -> Config:
        """获取配置管理"""
        if not self._config:
            self._config = JsonConfig(self)
        return self._config

    def dump_pkl(self, data: Any, filename: str, cache: bool = False, **kwargs) -> None:
        with self.open(filename, "wb", cache=cache) as f:
            pickle.dump(data, f, **kwargs)

    def load_pkl(self, filename: str, cache: bool = False, **kwargs) -> Any:
        with self.open(filename, "rb", cache=cache) as f:
            data = pickle.load(f, **kwargs)
        return data

    def dump_json(
        self,
        data: Any,
        filename: str,
        cache: bool = False,
        ensure_ascii: bool = False,
        **kwargs,
    ) -> None:
        with self.open(filename, "w", cache=cache, encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, **kwargs)

    def load_json(self, filename: str, cache: bool = False, **kwargs) -> Any:
        with self.open(filename, "r", cache=cache, encoding="utf8") as f:
            data = json.load(f, **kwargs)
        return data

    def open(self, filename: str, mode: str = "r", cache: bool = False, **kwargs) -> IO:
        """打开文件，默认打开数据文件夹下的文件"""
        if cache:
            path = self.cache_dir / filename
        else:
            path = self.data_dir / filename
        return open(path, mode, **kwargs)

    def exists(self, filename: str, cache: bool = False) -> bool:
        """判断文件是否存在，默认判断数据文件夹下的文件"""
        if cache:
            path = self.cache_dir / filename
        else:
            path = self.data_dir / filename
        return path.exists()

    async def download_file(
        self, url: str, filename: str, cache: bool = False, **kwargs
    ) -> bytes:
        """下载文件"""
        async with httpx.AsyncClient() as client:
            r = await client.get(url, **kwargs)
            content = r.content
            with self.open(filename, "wb", cache=cache) as f:
                f.write(content)
            logger.info(f"已下载文件 {url} -> {filename}")
            return content

    def network_file(
        self,
        url: str,
        filename: str,
        process_data: Optional[Callable[[T], R]] = None,
        cache: bool = False,
    ) -> NetworkFile[T, R]:
        """网络文件

        从网络上获取数据，并缓存至本地，仅支持 json 格式
        且可以在获取数据之后同时处理数据
        """
        return NetworkFile[T, R](url, filename, self, process_data, cache)

    @property
    def Model(self) -> Type[SQLModel]:
        """数据库模型"""
        if self._model is None:
            self._metadata = MetaData(info={"name": self.name})

            # 为每个插件创建一个独立的 registry
            plugin_registry = registry(metadata=self._metadata)

            class _SQLModel(SQLModel, registry=plugin_registry):
                @declared_attr
                def __tablename__(cls) -> str:
                    """设置表名前缀，避免表名冲突

                    规则为：插件名_表名
                    https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html#augmenting-the-base
                    """
                    return f"{self.name}_{cls.__name__.lower()}"

            self._model = _SQLModel
        return self._model

    @property
    def metadata(self) -> Optional[MetaData]:
        """获取数据库元数据"""
        return self._metadata

    @property
    def migration_dir(self) -> Optional[Path]:
        """数据库迁移文件夹"""
        if self._migration_path is None:
            plugin = get_plugin(self.name)
            if plugin and plugin.module.__file__ and PluginData(plugin.name).metadata:
                self._migration_path = (
                    Path(plugin.module.__file__).parent / "migrations"
                )
        return self._migration_path

    def set_migration_dir(self, path: Path) -> None:
        """设置数据库迁移文件夹"""
        self._migration_path = path


def get_plugin_data(name: Optional[str] = None) -> PluginData:
    """获取插件数据

    如果名称为空，则尝试自动获取调用者所在的插件名
    """
    name = name or get_caller_plugin_name()

    return PluginData(name)
