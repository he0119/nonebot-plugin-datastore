import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_open_data_file(app: App):
    """测试打开数据文件"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    test_file = plugin_config.datastore_data_dir / "test" / "test.txt"

    data = PluginData("test")

    assert test_file.exists() is False
    test_file.write_text("test")

    assert data.exists("test.txt") is True
    with data.open("test.txt", "r") as f:
        assert f.read() == "test"


@pytest.mark.asyncio
async def test_open_cache_file(app: App):
    """测试打开缓存文件"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    test_file = plugin_config.datastore_cache_dir / "test" / "test.txt"

    data = PluginData("test")

    assert test_file.exists() is False
    test_file.write_text("test")

    assert data.exists("test.txt", cache=True) is True
    with data.open("test.txt", "r", cache=True) as f:
        assert f.read() == "test"
