from typing import Optional

import click

from . import command


@click.group()
def cli():
    """Datastore CLI"""
    pass


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=(
        "Populate revision script with candidate migration "
        "operations, based on comparison of database to model"
    ),
)
def revision(name: Optional[str], message: Optional[str], autogenerate: bool):
    """revision"""
    command.revision(name=name, message=message, autogenerate=autogenerate)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.argument("revision", default="head")
def upgrade(name: Optional[str], revision: str):
    """upgrade"""
    command.upgrade(name=name, revision=revision)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.argument("revision", default="-1")
def downgrade(name: Optional[str], revision: str):
    """downgrade"""
    command.downgrade(name=name, revision=revision)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--rev-range", "-r", default=None, help="Revision range")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option(
    "--indicate-current",
    is_flag=True,
    help="Indicate current revisions with (head) and (current)",
)
def history(
    name: Optional[str],
    rev_range: Optional[str],
    verbose: bool,
    indicate_current: bool,
):
    """history"""
    command.history(
        name=name,
        rev_range=rev_range,
        verbose=verbose,
        indicate_current=indicate_current,
    )


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def current(name: Optional[str], verbose: bool):
    """current"""
    command.current(name=name, verbose=verbose)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def heads(name: Optional[str], verbose: bool):
    """heads"""
    command.heads(name=name, verbose=verbose)


@cli.command()
@click.option("--name", "-n", default=None, help="插件名")
def check(name: Optional[str]):
    """check"""
    command.check(name=name)


def main():
    cli()  # pragma: no cover
