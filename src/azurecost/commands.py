import click
import sys
from .core import Core
from . import constants


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False, help="enable debug logging")
@click.option("--subscription", "-s", type=str, required=True, help="gcp project id.")
@click.option("--resource-group", "-r", type=str, help="resource group.")
@click.option("--dimensions", "-d", multiple=True, default=constants.DEFAULT_DIMENSIONS, help="dimensions.")
@click.option("--granularity", "-g", type=str, default=constants.DEFAULT_GRANULARITY, help="granularity.")
@click.option("--ago", "-a", type=int, default=constants.DEFAULT_AGO, help="ago.")
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.pass_context
def cli(ctx, debug, subscription, resource_group, dimensions, granularity, ago, version):
    if version:
        print(constants.VERSION)
        sys.exit()
    core = Core(debug, granularity)
    total_results, results = core.get_usage(subscription, resource_group, dimensions, ago)
    print(core.convert_tabulate(total_results, results))


def main():
    cli(obj={})
