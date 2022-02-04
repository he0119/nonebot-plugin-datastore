import pytest
from nonebug import App
from pytest_mock import MockerFixture


def mocked_get(url: str, **kwargs):
    class MockResponse:
        def __init__(self, json: dict = None, content: bytes = None):
            self._json = json
            self._content = content

        def json(self):
            return self._json

        def content(self):
            return self._content

    if url == "http://example.com":
        return MockResponse(json={"key": "value"})

    return MockResponse({})


@pytest.mark.asyncio
async def test_cache_network_file(app: App, mocker: MockerFixture):
    """测试缓存网络文件至本地"""
    from nonebot_plugin_datastore import PluginData

    get = mocker.patch("httpx.AsyncClient.get", side_effect=mocked_get)

    plugin_data = PluginData("test")

    file = plugin_data.network_file("http://example.com", "test")

    data = await file.data
    assert data == {"key": "value"}

    # 确认文件是否缓存成功
    assert plugin_data.exists("test") is True
    assert plugin_data.load_json("test") == {"key": "value"}

    data = await file.data
    assert data == {"key": "value"}

    # 访问两次数据，但不会请求网络两次
    get.assert_called_once_with("http://example.com", timeout=30)
