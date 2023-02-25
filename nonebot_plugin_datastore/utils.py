import inspect
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

import pygtrie
from nonebot import get_loaded_plugins

if TYPE_CHECKING:
    from nonebot.plugin import Plugin


def get_caller_plugin_name() -> str:
    """获取当前函数调用者所在的插件名

    尝试自动获取调用者所在的插件名
    """
    name = None
    if frame := inspect.currentframe():
        # 因为是在插件内部调用，所以调用栈为
        # 1. 当前函数
        # 2. 调用者函数
        # 3. 调用者所在的插件
        # 需要往回跳两次
        frame = frame.f_back.f_back  # type: ignore
        if not frame:
            raise ValueError("无法找到调用者")  # pragma: no cover

        module_name = frame.f_locals["__name__"]
        plugin = _get_plugin_by_module_name(module_name)
        if plugin:
            name = plugin.name

    if not name:
        raise ValueError("自动获取插件名失败")

    return name


@lru_cache
def _get_plugin_by_module_name(module_name: str) -> Optional["Plugin"]:
    """通过模块名获取插件"""
    t = pygtrie.StringTrie(separator=".")
    for plugin in get_loaded_plugins():
        t[plugin.module_name] = plugin
    plugin = t.longest_prefix(module_name).value
    return plugin
