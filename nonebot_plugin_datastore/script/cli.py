import click

from .migrate import revision as _revision
from .migrate import upgrade as _upgrade


@click.group()
def cli():
    pass


@cli.command()
def revision():
    click.echo("Initialized the database")


def main():
    # cli()
    # _upgrade()
    _revision(message="test", autogenerate=True)
