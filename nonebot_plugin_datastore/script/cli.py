from typing import Optional

import click

from .migrate import revision as _revision
from .migrate import upgrade as _upgrade


@click.group()
def cli():
    """Datastore CLI"""
    pass


@cli.command()
@click.option("--name", "-n", default=None, help="Plugin name")
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
    _revision(name=name, message=message, autogenerate=autogenerate)


@cli.command()
@click.option("--name", "-n", default=None, help="Plugin name")
@click.argument("revision", default="head")
def upgrade(name: Optional[str], revision: str):
    """upgrade"""
    _upgrade(name=name, revision=revision)


def main():
    cli()
