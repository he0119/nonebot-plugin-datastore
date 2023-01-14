import asyncio
from pathlib import Path

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


def test_revision(app: App, tmp_path: Path):
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli

    require("tests.example2")
    asyncio.run(init_db())

    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ["revision", "--autogenerate", "--message", "test"])
        assert result.exit_code == 0
        assert "" in result.output


def test_upgrade(app: App):
    from nonebot import require

    from nonebot_plugin_datastore.script.cli import cli

    require("tests.example")

    runner = CliRunner()
    result = runner.invoke(cli, ["upgrade"])
    assert result.exit_code == 0
    assert "" in result.output


def test_downgrade(app: App):
    from nonebot import require

    from nonebot_plugin_datastore.db import init_db
    from nonebot_plugin_datastore.script.cli import cli

    require("tests.example")
    asyncio.run(init_db())

    runner = CliRunner()
    result = runner.invoke(cli, ["downgrade"])
    assert result.exit_code == 0
    assert "" in result.output
