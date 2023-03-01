from nonebug import App


async def test_singleton(app: App):
    """测试单例"""
    from nonebot_plugin_datastore import PluginData

    data1 = PluginData("test")
    data2 = PluginData("test")
    assert data1 is data2
    data1.config.set_sync("test", 1)
    assert data2.config.get_sync("test") == 1


async def test_singleton_keyword(app: App):
    """测试单例

    一个使用位置形参，一个使用关键字形参
    """
    from nonebot_plugin_datastore import PluginData

    data1 = PluginData("test")
    data2 = PluginData(name="test")
    assert data1 is data2
    data1.config.set_sync("test", 1)
    assert data2.config.get_sync("test") == 1


async def test_singleton_different(app: App):
    """测试单例

    不同名称的情况
    """
    from nonebot_plugin_datastore import PluginData

    data1 = PluginData("test")
    data2 = PluginData("test2")
    assert data1 is not data2
    data1.config.set_sync("test", 1)
    assert data2.config.get_sync("test") is None
