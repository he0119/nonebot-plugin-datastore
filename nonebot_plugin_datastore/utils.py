import importlib
import inspect
from typing import Any, Optional

from nonebot import get_plugin_by_module_name


def get_caller_plugin_name() -> str:
    """获取当前函数调用者所在的插件名

    尝试自动获取调用者所在的插件名
    """
    frame = inspect.currentframe()
    if frame is None:
        raise ValueError("无法获取当前栈帧")

    while frame := frame.f_back:
        module_name = (module := inspect.getmodule(frame)) and module.__name__
        if not module_name:
            raise ValueError("无法找到调用者")

        plugin = get_plugin_by_module_name(module_name)
        if plugin and plugin.name != "nonebot_plugin_datastore":
            return plugin.name

    raise ValueError("自动获取插件名失败")


def resolve_dot_notation(
    obj_str: str, default_attr: str, default_prefix: Optional[str] = None
) -> Any:
    """解析并导入点分表示法的对象"""
    modulename, _, cls = obj_str.partition(":")
    if default_prefix is not None and modulename.startswith("~"):
        modulename = default_prefix + modulename[1:]
    module = importlib.import_module(modulename)
    if not cls:
        return getattr(module, default_attr)
    instance = module
    for attr_str in cls.split("."):
        instance = getattr(instance, attr_str)
    return instance
