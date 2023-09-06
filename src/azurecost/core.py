from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryTimePeriod
from retrying import retry
from collections import defaultdict
from datetime import datetime
from tabulate import tabulate

from .logger import get_logger
from . import constants
from .date_util import DateUtil


class Core:
    def __init__(self, debug, granularity: str = constants.DEFAULT_GRANULARITY):
        self.subscription_client = SubscriptionClient(
            credential=AzureCliCredential()
        )
        self.cost_management_client = CostManagementClient(
            credential=AzureCliCredential()
        )
        self.logger = get_logger(debug)
        self.granularity = granularity

    @retry(stop_max_attempt_number=1, wait_fixed=10000)
    def get_usage(
            self,
            subscription_name: str,
            resource_group: str = None,
            dimensions: list = constants.DEFAULT_DIMENSIONS,
            ago: int = constants.DEFAULT_AGO,
        ):
        subscription = self.get_subscription_from_name(subscription_name)

        start, end = DateUtil.get_start_and_end(self.granularity, ago)
        def_period = QueryTimePeriod(from_property=start, to=end)

        scope = "/subscriptions/" + subscription.subscription_id
        if resource_group is not None:
            scope += "/resourceGroups/" + resource_group

        payload = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "time_period": def_period,
            "dataset": {
                "granularity": self.granularity,
                "aggregation": {
                    "totalCost": {"name": "PreTaxCost", "function": "Sum"},
                },
                # "grouping": grouping
            }
        }
        self.logger.debug(f"{start} - {end}")

        # total_cost
        usage = self.cost_management_client.query.usage(scope, payload)
        total_results = usage.rows
        self.logger.debug(total_results)

        payload["dataset"]["grouping"] = [
            {
                "type": "Dimension",
                "name": d
            }
            for d in dimensions
        ]
        usage = self.cost_management_client.query.usage(scope, payload)
        results = usage.rows
        self.logger.debug(results)

        return total_results, results

    def get_subscription_from_name(self, subscription_name: str):
        for subscription in self.subscription_client.subscriptions.list():
            if subscription.display_name != subscription_name:
                continue
            return subscription

    def convert_tabulate(self, total_results: list, results: list):
        dd = defaultdict(lambda: {})
        format_date = "%Y-%m" if self.granularity == "MONTHLY" else "%Y-%m-%d"

        for result in total_results:
            d = datetime.strptime(result[1], '%Y-%m-%dT%H:%M:%S').strftime(format_date)
            # 小数点を2桁にする
            dd["total"][d] = round(result[0], 2)

        for result in results:
            d = datetime.strptime(result[1], '%Y-%m-%dT%H:%M:%S').strftime(format_date)
            # 小数点を2桁にする
            dd[result[2]][d] = round(result[0], 2)

        costs = []
        for key, sum_costs in dd.items():
            d = {"key": key}
            d.update(sum_costs)
            costs.append(d)

        # 最近の月を取得
        last_time = list(costs[0].keys())[-1]

        # 最近の月でソート
        converts = sorted(
            costs,
            key=lambda x: 0 if x.get(last_time) is None else x.get(last_time),
            reverse=True,
        )
        return tabulate(converts, headers="keys")
