import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_singleton(app: App):
    """测试单例"""
    from nonebot_plugin_datastore import PluginData

    data1 = PluginData("test")
    data2 = PluginData("test")
    assert data1 is data2
    data1.config.set("test", 1)
    assert data2.config.get("test") == 1


@pytest.mark.asyncio
async def test_singleton_different(app: App):
    """测试单例"""
    from nonebot_plugin_datastore import PluginData

    data1 = PluginData("test")
    data2 = PluginData("test2")
    assert data1 is not data2
    data1.config.set("test", 1)
    assert data2.config.get("test") is None
