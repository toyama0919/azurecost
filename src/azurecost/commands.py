import click
import sys
from .core import Core
from . import constants


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug logging to see detailed request/response information.",
)
@click.option(
    "--subscription",
    "-s",
    type=str,
    help="Azure subscription display name. Can be omitted if AZURE_SUBSCRIPTION_ID environment variable is set.",
)
@click.option(
    "--resource-group",
    "-r",
    type=str,
    help="Filter costs by a specific resource group. Can be omitted if AZURE_RESOURCE_GROUP environment variable is set.",
)
@click.option(
    "--dimensions",
    "-d",
    type=click.Choice(constants.AVAILABLE_DIMENSIONS),
    multiple=True,
    default=constants.DEFAULT_DIMENSIONS,
    help="Dimensions to aggregate costs by (e.g., ResourceGroup, ServiceName). Can be specified multiple times. Default: ServiceName.",
)
@click.option(
    "--granularity",
    "-g",
    type=click.Choice(constants.AVAILABLE_GRANULARITY),
    default=constants.DEFAULT_GRANULARITY,
    help="Time granularity for cost aggregation. Use MONTHLY for monthly costs or DAILY for daily costs. Default: MONTHLY.",
)
@click.option(
    "--ago",
    "-a",
    type=int,
    default=constants.DEFAULT_AGO,
    help="Number of periods (months for MONTHLY, days for DAILY) to look back from today. For example, use 3 to get the past 3 months. Default: 1.",
)
@click.option(
    "--version/--no-version",
    "-v",
    default=False,
    help="Display the version number and exit.",
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
