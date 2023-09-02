from pathlib import Path

import pytest
from click.testing import CliRunner
from nonebug import App


def test_cli_help(app: App):
    from nonebot_plugin_datastore.script.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output
    assert "revision" in result.output
    assert "upgrade" in result.output
    assert "downgrade" in result.output

    result = runner.invoke(cli, ["revision", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "--autogenerate" in result.output
    assert "--message" in result.output

    result = runner.invoke(cli, ["upgrade", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "[REVISION]" in result.output

    result = runner.invoke(cli, ["downgrade", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "[REVISION]" in result.output


@pytest.mark.anyio
async def test_revision(app: App, tmp_path: Path):
    from nonebot import require

    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")
    require("tests.example.plugin2")
    await init_db()

    runner = CliRunner()

    # 测试跳过生成迁移文件
    result = await run_sync(runner.invoke)(
        cli, ["revision", "--autogenerate", "--name", "plugin1"]
    )
    assert result.exit_code == 0
    assert result.output == ""

    # 手动设置迁移文件目录
    PluginData("plugin2").set_migration_dir(tmp_path / "revision")

    # 测试生成迁移文件
    migration_dir = tmp_path / "revision"
    assert migration_dir
    assert not migration_dir.exists()

    result = await run_sync(runner.invoke)(
        cli, ["revision", "--autogenerate", "--name", "plugin2", "-m", "test"]
    )
    assert result.exit_code == 0
    assert "Generating" in result.output
    assert "test.py" in result.output

    assert migration_dir.exists()

    # 测试插件如果不在项目目录下，会报错
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = await run_sync(runner.invoke)(cli, ["revision", "--name", "plugin2"])
        assert result.exit_code == 2
        assert "未找到插件" in result.output


@pytest.mark.anyio
async def test_migrate(app: App, tmp_path: Path):
    from nonebot import require

    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")
    require("tests.example.plugin2")
    await init_db()

    runner = CliRunner()

    # 测试跳过生成迁移文件
    result = await run_sync(runner.invoke)(cli, ["migrate", "--name", "plugin1"])
    assert result.exit_code == 0
    assert result.output == ""

    # 手动设置迁移文件目录
    PluginData("plugin2").set_migration_dir(tmp_path / "revision")

    # 测试生成迁移文件
    migration_dir = tmp_path / "revision"
    assert migration_dir
    assert not migration_dir.exists()

    result = await run_sync(runner.invoke)(
        cli, ["migrate", "--name", "plugin2", "-m", "test"]
    )
    assert result.exit_code == 0
    assert "Generating" in result.output
    assert "test.py" in result.output

    assert migration_dir.exists()


@pytest.mark.anyio
async def test_upgrade(app: App):
    from nonebot import require

    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")

    runner = CliRunner()
    result = await run_sync(runner.invoke)(cli, ["upgrade"])
    assert result.exit_code == 0
    assert result.output == ""

    require("tests.example.pre_db_init_error")
    result = await run_sync(runner.invoke)(cli, ["upgrade"])
    assert result.exit_code == 1
    assert result.output == ""


@pytest.mark.anyio
async def test_upgrade_single_plugin(app: App):
    """测试单独升级某个插件"""
    from nonebot import require

    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")
    require("tests.example.pre_db_init_error")

    runner = CliRunner()
    result = await run_sync(runner.invoke)(cli, ["upgrade", "--name", "plugin1"])
    assert result.exit_code == 0
    assert result.output == ""

    result = await run_sync(runner.invoke)(
        cli, ["upgrade", "--name", "pre_db_init_error"]
    )
    assert result.exit_code == 1
    assert result.output == ""


@pytest.mark.anyio
async def test_downgrade(app: App):
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")
    await init_db()

    runner = CliRunner()
    result = await run_sync(runner.invoke)(cli, ["downgrade"])
    assert result.exit_code == 0
    assert result.output == ""


@pytest.mark.anyio
async def test_other_commands(app: App):
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin1")
    require("tests.example.plugin2")

    runner = CliRunner()
    result = await run_sync(runner.invoke)(cli, ["history"])
    assert result.exit_code == 0
    assert result.output == ""

    result = await run_sync(runner.invoke)(cli, ["current"])
    assert result.exit_code == 0
    assert result.output == ""

    result = await run_sync(runner.invoke)(cli, ["heads"])
    assert result.exit_code == 0
    assert result.output == ""

    result = await run_sync(runner.invoke)(cli, ["check"])
    assert result.exit_code == 1
    assert result.output == ""

    await init_db()

    result = await run_sync(runner.invoke)(cli, ["check", "--name", "plugin1"])
    assert result.exit_code == 0
    assert result.output == ""

    result = await run_sync(runner.invoke)(cli, ["dir"])
    assert result.exit_code == 0
    assert "当前存储路径:" in result.output

    result = await run_sync(runner.invoke)(cli, ["dir", "--name", "plugin1"])
    assert result.exit_code == 0
    assert "插件 plugin1 的存储路径:" in result.output


@pytest.mark.anyio
async def test_revision_path_with_space(app: App, tmp_path: Path):
    """测试迁移文件目录路径中包含空格时的情况"""
    from nonebot import require

    from nonebot_plugin_datastore import PluginData
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.example.plugin2")

    runner = CliRunner()

    # 手动设置迁移文件目录
    migration_dir = tmp_path / "revision test"
    PluginData("plugin2").set_migration_dir(migration_dir)

    # 测试生成迁移文件
    assert migration_dir
    assert not migration_dir.exists()

    result = await run_sync(runner.invoke)(
        cli, ["revision", "--autogenerate", "--name", "plugin2", "-m", "test"]
    )
    assert result.exit_code == 0
    assert "Generating" in result.output
    assert "test.py" in result.output

    assert migration_dir.exists()


@pytest.mark.anyio
async def test_migrate_global_registry(app: App, tmp_path: Path):
    """测试使用全局注册表的插件迁移

    确保可以识别到对应插件的模型
    """
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli, run_sync

    require("tests.registry.plugin3")
    require("tests.registry.plugin3_plugin4")
    await init_db()

    runner = CliRunner()

    # 测试跳过生成迁移文件
    result = await run_sync(runner.invoke)(cli, ["migrate", "--name", "plugin3"])
    assert result.exit_code == 0
    assert result.output == ""
