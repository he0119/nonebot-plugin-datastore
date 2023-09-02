from nonebug import App


async def test_exists(app: App):
    """测试文件是否存在"""
    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.config import plugin_config

    data = PluginData("test")

    test_file = plugin_config.datastore_data_dir / "test" / "data"
    assert test_file.exists() is False
    assert data.exists("data") is False
    test_file.touch()
    assert test_file.exists() is True
    assert data.exists("data") is True

    test_file = plugin_config.datastore_cache_dir / "test" / "cache"
    assert test_file.exists() is False
    assert data.exists("cache", cache=True) is False
    test_file.touch()
    assert test_file.exists() is True
    assert data.exists("cache", cache=True) is True


async def test_open_file(app: App):
    """测试打开文件"""
    from nonebot_plugin_datastore import PluginData

    data = PluginData("test")

    test_file = data.data_dir / "test.txt"
    assert test_file.exists() is False
    test_file.write_text("test")

    with data.open("test.txt", "r") as f:
        assert f.read() == "test"

    test_file = data.cache_dir / "test.txt"
    assert test_file.exists() is False
    test_file.write_text("test")

    with data.open("test.txt", "r", cache=True) as f:
        assert f.read() == "test"


async def test_dump_load_data(app: App):
    """测试 dump 和 load 数据"""
    from nonebot_plugin_datastore import PluginData

    data = PluginData("test")

    test = {"test": 1}
    data.dump_pkl(test, "test.pkl")
    assert data.exists("test.pkl") is True
    assert data.load_pkl("test.pkl") == test

    test = {"test": 2}
    data.dump_pkl(test, "test.pkl", cache=True)
    assert data.exists("test.pkl", cache=True) is True
    assert data.load_pkl("test.pkl", cache=True) == test

    test = {"test": 3}
    data.dump_json(test, "test.json")
    assert data.exists("test.json") is True
    assert data.load_json("test.json") == test

    test = {"test": 4}
    data.dump_json(test, "test.json", cache=True)
    assert data.exists("test.json", cache=True) is True
    assert data.load_json("test.json", cache=True) == test
