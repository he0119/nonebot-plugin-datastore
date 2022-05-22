import json
from typing import Optional

import pytest
from nonebug import App
from pytest_mock import MockerFixture


async def mocked_get(url: str, **kwargs):
    class MockResponse:
        def __init__(self, json: Optional[dict] = None):
            self._json = json

        def json(self):
            return self._json

        @property
        def content(self):
            if self._json:
                return json.dumps(self._json).encode("utf-8")

    if url == "http://example.com":
        return MockResponse(json={"key": "值"})

    return MockResponse({})


@pytest.mark.asyncio
async def test_cache_network_file(app: App, mocker: MockerFixture):
    """测试缓存网络文件至本地"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")

    file = plugin_data.network_file("http://example.com", "test")

    data = await file.data
    assert data == {"key": "值"}

    # 确认文件是否缓存成功
    assert plugin_data.exists("test") is True
    assert plugin_data.load_json("test") == {"key": "值"}

    data = await file.data
    assert data == {"key": "值"}

    # 访问两次数据，因为缓存，所以不会请求网络两次
    get.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_load_local_file(app: App, mocker: MockerFixture):
    """测试读取本地文件"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")
    plugin_data.dump_json({"key": "值"}, "test")

    file = plugin_data.network_file("http://example.com", "test")

    data = await file.data
    assert data == {"key": "值"}

    # 访问数据，因为会读取本地文件，所以不会请求网络
    get.assert_not_called()


@pytest.mark.asyncio
async def test_process_data(app: App, mocker: MockerFixture):
    """测试处理数据"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")
    plugin_data.dump_json({"key": "值"}, "test")

    def test_process(data: dict):
        data["key2"] = "值2"
        return data

    file = plugin_data.network_file(
        "http://example.com", "test", process_data=test_process
    )

    data = await file.data
    assert data == {"key": "值", "key2": "值2"}

    data = await file.data
    assert data == {"key": "值", "key2": "值2"}

    # 访问数据，因为会读取本地文件，所以不会请求网络
    get.assert_not_called()


@pytest.mark.asyncio
async def test_update_data(app: App, mocker: MockerFixture):
    """测试更新数据"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")
    plugin_data.dump_json({"key": "old"}, "test")

    file = plugin_data.network_file("http://example.com", "test")

    # 读取的本地文件
    data = await file.data
    assert data == {"key": "old"}

    await file.update()

    # 更新之后，就是从服务器获取的最新数据
    data = await file.data
    assert data == {"key": "值"}

    get.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_download_file(app: App, mocker: MockerFixture):
    """测试下载文件"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")

    file = await plugin_data.download_file("http://example.com", "test")

    with plugin_data.open("test", "rb") as f:
        data = f.read()

    assert file == data

    get.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_download_file_with_kwargs(app: App, mocker: MockerFixture):
    """测试下载文件，附带参数"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")

    data = await plugin_data.download_file("http://example.com", "test", timeout=30)

    with plugin_data.open("test", "rb") as f:
        assert data == f.read()

    get.assert_called_once_with("http://example.com", timeout=30)
