import pytest
from nonebug import App


async def test_get_plugin_data_failed(app: App):
    """获取插件数据失败"""
    from nonebot_plugin_datastore import get_plugin_data

    # 不在插件中调用
    with pytest.raises(ValueError, match="自动获取插件名失败"):
        get_plugin_data()

    # 没有加载插件直接使用
    with pytest.raises(ValueError, match="无法找到调用者"):
        import tests.example.plugin1  # noqa: F401


async def test_plugin_dir_is_file(app: App):
    """插件数据文件夹已经存在且为文件"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    plugin_config.datastore_data_dir.mkdir(parents=True, exist_ok=True)
    plugin_dir = plugin_config.datastore_data_dir / "test"
    plugin_dir.touch()
    assert plugin_dir.is_file()

    data = PluginData("test")
    with pytest.raises(RuntimeError):
        data.data_dir
