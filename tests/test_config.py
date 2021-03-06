import json

import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_read_config(app: App):
    """测试读取配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    plugin_config.datastore_config_dir.mkdir(exist_ok=True)

    config_file = plugin_config.datastore_config_dir / "test.json"
    with open(config_file, "w", encoding="utf8") as f:
        json.dump({"test": 1}, f)

    data = PluginData("test")
    assert data.config.get("test") == 1


@pytest.mark.asyncio
async def test_write_config(app: App):
    """测试写入配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    config_file = plugin_config.datastore_config_dir / "test.json"
    assert config_file.exists() is False

    data = PluginData("test")
    data.config.set("test", 1)

    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
        assert data["test"] == 1
