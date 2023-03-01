import json

import pytest
from nonebug import App


async def test_read_config(app: App):
    """测试读取配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    plugin_config.datastore_config_dir.mkdir(exist_ok=True)

    config_file = plugin_config.datastore_config_dir / "test.json"
    with open(config_file, "w", encoding="utf8") as f:
        json.dump({"test": 1}, f)

    data = PluginData("test")
    assert data.config.get_sync("test") == 1
    assert await data.config.get("test") == 1


async def test_write_config(app: App):
    """测试写入配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    config_file = plugin_config.datastore_config_dir / "test.json"
    assert config_file.exists() is False

    data = PluginData("test")
    await data.config.set("async", 1)
    data.config.set_sync("sync", 2)

    with open(config_file, encoding="utf8") as f:
        data = json.load(f)
        assert data["async"] == 1
        assert data["sync"] == 2


async def test_write_config_while_folder_deleted(app: App):
    """测试删除文件夹后写入配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    config_file = plugin_config.datastore_config_dir / "test.json"
    assert config_file.exists() is False

    data = PluginData("test")
    await data.config.set("test", 1)

    assert config_file.exists() is True

    config_file.unlink()
    plugin_config.datastore_config_dir.rmdir()

    await data.config.set("test", 1)


@pytest.mark.parametrize(
    "app",
    [
        pytest.param({"datastore_config_provider": "~json"}, id="json"),
        pytest.param({"datastore_config_provider": "~database"}, id="database"),
        pytest.param({"datastore_config_provider": "~toml"}, id="toml"),
        pytest.param({"datastore_config_provider": "~yaml"}, id="yaml"),
    ],
    indirect=True,
)
async def test_read_write_config(app: App):
    """测试读写配置"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.providers.database import Config

    data = PluginData("test")
    if isinstance(data.config, Config):
        await init_db()

    simple = 1
    await data.config.set("test", simple)
    assert await data.config.get("test") == simple

    complex = {"a": 1, "b": [1, 2, 3], "c": {"d": 1}}
    await data.config.set("test", complex)
    assert await data.config.get("test") == complex
