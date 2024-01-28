import click
import sys
from .core import Core
from . import constants


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False, help="enable debug logging")
@click.option("--subscription", "-s", type=str, help="subscription display name.")
@click.option("--resource-group", "-r", type=str, help="resource group.")
@click.option(
    "--dimensions",
    "-d",
    type=click.Choice(constants.AVAILABLE_DIMENSIONS),
    multiple=True,
    default=constants.DEFAULT_DIMENSIONS,
    help="dimensions.",
)
@click.option(
    "--granularity",
    "-g",
    type=click.Choice(constants.AVAILABLE_GRANULARITY),
    default=constants.DEFAULT_GRANULARITY,
    help="granularity.",
)
@click.option("--ago", "-a", type=int, default=constants.DEFAULT_AGO, help="ago.")
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.pass_context
def cli(
    ctx, debug, subscription, resource_group, dimensions, granularity, ago, version
):
    if version:
        print(constants.VERSION)
        sys.exit()
    core = Core(debug, granularity, dimensions, subscription, resource_group)
    total_results, results = core.get_usage(ago)
    click.echo(core.convert_tabulate(total_results, results))


def main():
    cli(obj={})
