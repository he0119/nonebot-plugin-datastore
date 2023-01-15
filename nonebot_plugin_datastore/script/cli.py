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


def main():
    cli()  # pragma: no cover
