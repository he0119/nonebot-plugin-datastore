from typing import Optional

import click

from .migrate import revision as _revision
from .migrate import upgrade as _upgrade


@click.group()
def cli():
    """Datastore CLI"""
    pass


@cli.command()
@click.option("--name", "-n", help="Plugin name")
@click.option("--autogenerate", is_flag=True, help="Autogenerate")
def revision(name: Optional[str], autogenerate: bool):
    """revision"""
    click.echo(f"revision {name=}, {autogenerate=}")
    _revision(name=name, autogenerate=autogenerate)


@cli.command()
@click.option("--name", "-n", help="Plugin name")
def upgrade(name: Optional[str]):
    """upgrade"""
    click.echo(f"upgrade {name=}")
    _upgrade(name=name)


def main():
    cli()
