from azure.identity import DefaultAzureCredential

# SubscriptionClient moved out of the azure.mgmt.resource top level in
# azure-mgmt-resource 25.0.0, where it was split into the separate
# azure-mgmt-resource-subscriptions distribution. The azure.mgmt.resource.subscriptions
# path works on both the older bundled layout and the new split one.
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryAggregation,
    QueryDataset,
    QueryDefinition,
    QueryGrouping,
    QueryTimePeriod,
)
from collections import defaultdict
from datetime import datetime
from tabulate import tabulate
import os
import uuid

from .logger import get_logger
from . import constants
from .date_util import DateUtil


class Core:
    def __init__(
        self,
        debug,
        granularity: str = constants.DEFAULT_GRANULARITY,
        dimensions: list = constants.DEFAULT_DIMENSIONS,
        subscription_name: str = None,
        resource_group: str = None,
        credential=None,
        cost_management_client=None,
        subscription_client=None,
    ):
        self.credential = credential or DefaultAzureCredential()
        self.cost_management_client = cost_management_client or CostManagementClient(
            self.credential,
            # ClientType header with unique UUID is required to prevent "429 Too Many Requests" errors.
            # Azure Cost Management API tracks clients by this header. Without a unique identifier,
            # multiple requests from the same client instance are treated as a single client,
            # causing rate limiting to be applied more aggressively and leading to 429 errors.
            # By using a unique UUID per client instance, each instance is tracked separately,
            # allowing rate limits to be distributed across instances rather than concentrated on one.
            headers={"ClientType": str(uuid.uuid4())},
            logging_enable=True,  # Enable request/response logging for debugging
        )
        self._subscription_client = subscription_client
        self.logger = get_logger(debug)
        self.granularity = granularity
        self.dimensions = dimensions
        self.subscription_id = self._get_subscription_id(subscription_name)
        self.resource_group = (
            resource_group if resource_group else os.environ.get("AZURE_RESOURCE_GROUP")
        )

    def get_usage(
        self,
        ago: int = constants.DEFAULT_AGO,
    ):
        start, end = DateUtil.get_start_and_end(self.granularity, ago)
        time_period = QueryTimePeriod(from_property=start, to=end)

        scope = "/subscriptions/" + self.subscription_id
        if self.resource_group:
            scope += "/resourceGroups/" + self.resource_group

        self.logger.debug(f"{start} - {end}")
        self.logger.debug(f"time_period = {time_period}")
        self.logger.debug(f"scope = {scope}")

        # total_cost
        total_query = self._build_query(time_period)
        self.logger.debug(f"total_query = {total_query}")
        usage = self.cost_management_client.query.usage(scope, total_query)
        columns = list(map(lambda col: col.name, usage.columns))
        total_results = [dict(zip(columns, row)) for row in usage.rows]
        self.logger.debug(f"total_results = {total_results}")

        # cost by dimensions
        dimension_query = self._build_query(
            time_period,
            grouping=[QueryGrouping(type="Dimension", name=d) for d in self.dimensions],
        )
        self.logger.debug(f"dimension_query = {dimension_query}")
        usage = self.cost_management_client.query.usage(scope, dimension_query)
        columns = list(map(lambda col: col.name, usage.columns))
        results = [dict(zip(columns, row)) for row in usage.rows]
        self.logger.debug(f"results = {results}")
        return total_results, results

    def _build_query(self, time_period: QueryTimePeriod, grouping: list = None):
        """Build a QueryDefinition for the cost management query API.

        The payload is built from the SDK models rather than a plain dict because
        azure-mgmt-costmanagement 5.0.0 stopped translating snake_case keys of a raw
        dict, which made the server reject the request with
        "Invalid query definition: Valid TimePeriod with range not exceeding one year
        must be present."
        """
        return QueryDefinition(
            type="ActualCost",
            timeframe="Custom",
            time_period=time_period,
            dataset=QueryDataset(
                granularity=self.granularity,
                aggregation={
                    "totalCost": QueryAggregation(name="Cost", function="Sum")
                },
                grouping=grouping,
            ),
        )

    def convert_tabulate(self, total_results: list, results: list):
        dd = defaultdict(lambda: {})
        view_format_date = "%Y-%m" if self.granularity == "MONTHLY" else "%Y-%m-%d"
        format_date = "%Y-%m-%dT%H:%M:%S" if self.granularity == "MONTHLY" else "%Y%m%d"
        date_key = "BillingMonth" if self.granularity == "MONTHLY" else "UsageDate"
        currency = results[0].get("Currency") if results else "USD"

        for result in total_results:
            d = datetime.strptime(str(result[date_key]), format_date).strftime(
                view_format_date
            )
            # Set the decimal point to two digits.
            dd["total"][d] = round(result["Cost"], 2)

        for result in results:
            d = datetime.strptime(str(result[date_key]), format_date).strftime(
                view_format_date
            )
            # Set the decimal point to two digits.
            dimensions = ", ".join([result[dimension] for dimension in self.dimensions])
            dd[dimensions][d] = round(result["Cost"], 2)

        costs = []
        for raw_key, sum_costs in dd.items():
            key = raw_key.replace(f"/subscriptions/{self.subscription_id}", "")
            if self.resource_group:
                key = key.replace(f"/resourcegroups/{self.resource_group}", "")
            d = {
                f"({currency})": key.replace(
                    f"/subscriptions/{self.subscription_id}", ""
                )
            }
            d.update(sum_costs)
            costs.append(d)

        if not costs:
            return "No data available."

        # Get the most recent month
        last_time = list(costs[0].keys())[-1]

        # Sort by most recent month
        converts = sorted(
            costs,
            key=lambda x: 0 if x.get(last_time) is None else x.get(last_time),
            reverse=True,
        )
        return tabulate(converts, headers="keys")

    def _get_subscription_id(self, subscription_name: str = None):
        if subscription_name:
            if self._subscription_client is None:
                self._subscription_client = SubscriptionClient(
                    credential=self.credential
                )
            for subscription in self._subscription_client.subscriptions.list():
                if subscription.display_name != subscription_name:
                    continue
                return subscription.subscription_id
            raise ValueError(f"Subscription '{subscription_name}' not found.")
        elif os.environ.get("AZURE_SUBSCRIPTION_ID"):
            return os.environ.get("AZURE_SUBSCRIPTION_ID")
        else:
            raise ValueError("Subscription name is required.")
