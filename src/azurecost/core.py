from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryTimePeriod
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
    ):
        credential = DefaultAzureCredential()
        self.subscription_client = SubscriptionClient(credential=credential)
        self.cost_management_client = CostManagementClient(
            credential,
            headers={"ClientType": str(uuid.uuid4())},
            logging_enable=True,
        )
        self.logger = get_logger(debug)
        self.granularity = granularity
        self.dimensions = dimensions
        self.subscription_id = (
            self._get_subscription_from_name(subscription_name).subscription_id
            if os.environ.get("AZURE_SUBSCRIPTION_ID") is None
            else os.environ.get("AZURE_SUBSCRIPTION_ID")
        )
        self.resource_group = resource_group

    def get_usage(
        self,
        ago: int = constants.DEFAULT_AGO,
    ):
        start, end = DateUtil.get_start_and_end(self.granularity, ago)
        time_period = QueryTimePeriod(from_property=start, to=end)

        scope = "/subscriptions/" + self.subscription_id
        if self.resource_group is not None:
            scope += "/resourceGroups/" + self.resource_group

        payload = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "time_period": time_period,
            "dataset": {
                "granularity": self.granularity,
                "aggregation": {
                    "totalCost": {"name": "Cost", "function": "Sum"},
                },
            },
        }
        self.logger.debug(f"{start} - {end}")

        # total_cost
        self.logger.debug(f"time_period = {time_period}")
        self.logger.debug(f"scope = {scope}")
        self.logger.debug(f"payload = {payload}")
        usage = self.cost_management_client.query.usage(scope, payload)
        columns = list(map(lambda col: col.name, usage.columns))
        total_results = [dict(zip(columns, row)) for row in usage.rows]
        self.logger.debug(f"total_results = {total_results}")

        # cost by dimensions
        payload["dataset"]["grouping"] = [
            {"type": "Dimension", "name": d} for d in self.dimensions
        ]
        self.logger.debug(f"payload = {payload}")
        usage = self.cost_management_client.query.usage(scope, payload)
        columns = list(map(lambda col: col.name, usage.columns))
        results = [dict(zip(columns, row)) for row in usage.rows]
        self.logger.debug(f"results = {results}")
        return total_results, results

    def convert_tabulate(self, total_results: list, results: list):
        dd = defaultdict(lambda: {})
        view_format_date = "%Y-%m" if self.granularity == "MONTHLY" else "%Y-%m-%d"
        format_date = "%Y-%m-%dT%H:%M:%S" if self.granularity == "MONTHLY" else "%Y%m%d"
        date_key = "BillingMonth" if self.granularity == "MONTHLY" else "UsageDate"
        currency = results[0].get("Currency")

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
            if self.resource_group is not None:
                key = key.replace(f"/resourcegroups/{self.resource_group}", "")
            d = {
                f"({currency})": key.replace(
                    f"/subscriptions/{self.subscription_id}", ""
                )
            }
            d.update(sum_costs)
            costs.append(d)

        # Get the most recent month
        last_time = list(costs[0].keys())[-1]

        # Sort by most recent month
        converts = sorted(
            costs,
            key=lambda x: 0 if x.get(last_time) is None else x.get(last_time),
            reverse=True,
        )
        return tabulate(converts, headers="keys")

    def _get_subscription_from_name(self, subscription_name: str):
        for subscription in self.subscription_client.subscriptions.list():
            if subscription.display_name != subscription_name:
                continue
            return subscription
