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


async def test_global_registry(app: App):
    """测试全局注册"""
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db

    require("tests.registry.plugin3")
    require("tests.registry.plugin4")

    from tests.registry.plugin4 import Example

    await init_db()

    Example(message="matcher")
