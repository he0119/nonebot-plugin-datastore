from nonebug import App


async def test_registry(app: App):
    """测试注册"""
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db

    require("tests.registry.plugin1")
    require("tests.registry.plugin2")

    from tests.registry.plugin1 import Example

    await init_db()

    Example(message="matcher")
