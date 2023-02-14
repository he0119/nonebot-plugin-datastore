import pytest
from nonebug import App


async def test_get_plugin_data_failed(app: App):
    """获取插件数据失败"""
    from nonebot_plugin_datastore import get_plugin_data

    # f_locals 中没有 __name__
    with pytest.raises(KeyError):
        get_plugin_data()

    # 没有加载插件直接使用
    with pytest.raises(ValueError) as e:
        import tests.example

    assert e.value.args[0] == "插件名称为空，且自动获取失败"


async def test_plugin_dir_is_file(app: App):
    """插件数据文件夹已经存在且为文件"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    plugin_dir = plugin_config.datastore_data_dir / "test"
    plugin_dir.touch()
    assert plugin_dir.is_file()

    data = PluginData("test")
    with pytest.raises(RuntimeError):
        data.data_dir
