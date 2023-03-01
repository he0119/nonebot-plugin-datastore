import abc
from typing import TYPE_CHECKING, Any, Coroutine, TypeVar, Union, overload

if TYPE_CHECKING:
    from ..plugin import PluginData

T = TypeVar("T")
R = TypeVar("R")


class ConfigProvider(abc.ABC):
    """插件配置管理"""

    def __init__(self, plugin_data: "PluginData") -> None:
        self._plugin_data = plugin_data

    @abc.abstractmethod
    def _get_sync(self, key: str) -> Any:
        """获取配置键值"""
        # TODO: 支持从数据库读取数据
        raise NotImplementedError

    @abc.abstractmethod
    def _set_sync(self, key: str, value: Any) -> None:
        """设置配置键值"""
        raise NotImplementedError

    @abc.abstractmethod
    async def _get(self, key: str) -> Any:
        """获取配置键值"""
        raise NotImplementedError

    @abc.abstractmethod
    async def _set(self, key: str, value: Any) -> None:
        """异步设置配置键值"""
        raise NotImplementedError

    @overload
    def get_sync(self, __key: str) -> Union[Any, None]:
        ...

    @overload
    def get_sync(self, __key: str, __default: T) -> T:
        ...

    def get_sync(self, key, default=None):
        """获得配置

        如果配置获取失败则使用 `default` 值并保存
        如果不提供 `default` 默认返回 None
        """
        try:
            value = self._get_sync(key)
        except:
            value = default
            # 保存默认配置
            self.set_sync(key, value)
        return value

    def set_sync(self, key: str, value: Any) -> None:
        """设置配置"""
        self._set_sync(key, value)

    @overload
    async def get(self, __key: str) -> Union[Any, None]:
        ...

    @overload
    async def get(self, __key: str, __default: T) -> T:
        ...

    async def get(self, key, default=None):
        """获得配置

        如果配置获取失败则使用 `default` 值并保存
        如果不提供 `default` 默认返回 None
        """
        try:
            value = await self._get(key)
        except:
            value = default
            # 保存默认配置
            await self.set(key, value)
        return value

    async def set(self, key: str, value: Any) -> None:
        """设置配置"""
        await self._set(key, value)
