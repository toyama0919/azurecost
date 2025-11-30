import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from azurecost.core import Core
from azurecost import constants


class TestCoreConvertTabulate:
    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_monthly_single_dimension(self):
        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        total_results = [
            {"BillingMonth": "2023-08-01T00:00:00", "Cost": 492.77},
            {"BillingMonth": "2023-09-01T00:00:00", "Cost": 80.28},
        ]
        results = [
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 492.77,
                "ServiceName": "Cognitive Services",
                "Currency": "USD",
            },
            {
                "BillingMonth": "2023-09-01T00:00:00",
                "Cost": 80.28,
                "ServiceName": "Cognitive Services",
                "Currency": "USD",
            },
        ]

        output = core.convert_tabulate(total_results, results)
        assert "total" in output
        assert "Cognitive Services" in output
        assert "2023-08" in output
        assert "2023-09" in output
        assert "492.77" in output
        assert "80.28" in output

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_daily(self):
        core = Core(
            False,
            granularity="DAILY",
            dimensions=["ServiceName"],
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        total_results = [
            {"UsageDate": "20230901", "Cost": 10.5},
            {"UsageDate": "20230902", "Cost": 20.3},
        ]
        results = [
            {
                "UsageDate": "20230901",
                "Cost": 10.5,
                "ServiceName": "Storage",
                "Currency": "USD",
            },
            {
                "UsageDate": "20230902",
                "Cost": 20.3,
                "ServiceName": "Storage",
                "Currency": "USD",
            },
        ]

        output = core.convert_tabulate(total_results, results)
        assert "total" in output
        assert "Storage" in output
        assert "2023-09-01" in output
        assert "2023-09-02" in output

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_multiple_dimensions(self):
        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ResourceGroup", "ServiceName"],
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        total_results = [
            {"BillingMonth": "2023-08-01T00:00:00", "Cost": 492.77},
        ]
        results = [
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 281.0,
                "ResourceGroup": "RG-1",
                "ServiceName": "Cognitive Services",
                "Currency": "USD",
            },
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 211.77,
                "ResourceGroup": "RG-2",
                "ServiceName": "Cognitive Services",
                "Currency": "USD",
            },
        ]

        output = core.convert_tabulate(total_results, results)
        assert "RG-1" in output
        assert "RG-2" in output
        assert "Cognitive Services" in output

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_empty_results(self):
        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        output = core.convert_tabulate([], [])
        assert output == "No data available."

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_with_resource_group(self):
        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            resource_group="test-rg",
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        total_results = [
            {"BillingMonth": "2023-08-01T00:00:00", "Cost": 100.0},
        ]
        results = [
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 100.0,
                "ServiceName": "Storage",
                "Currency": "USD",
            },
        ]

        output = core.convert_tabulate(total_results, results)
        assert "Storage" in output
        assert "100" in output  # tabulate may format as integer

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_convert_tabulate_rounds_to_two_decimals(self):
        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            cost_management_client=Mock(),
        )
        core.subscription_id = "test-sub-id"

        total_results = [
            {"BillingMonth": "2023-08-01T00:00:00", "Cost": 123.456789},
        ]
        results = [
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 123.456789,
                "ServiceName": "Storage",
                "Currency": "USD",
            },
        ]

        output = core.convert_tabulate(total_results, results)
        # Should round to 2 decimal places
        assert "123.46" in output or "123.45" in output


class TestCoreGetSubscriptionId:
    def test_get_subscription_id_from_name(self):
        mock_subscription = Mock()
        mock_subscription.display_name = "test-subscription"
        mock_subscription.subscription_id = "test-sub-id-123"

        mock_subscription_client = Mock()
        mock_subscription_client.subscriptions.list.return_value = [mock_subscription]

        core = Core(
            False,
            subscription_name="test-subscription",
            cost_management_client=Mock(),
            subscription_client=mock_subscription_client,
        )
        assert core.subscription_id == "test-sub-id-123"

    def test_get_subscription_id_from_env(self):
        with patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "env-sub-id-456"}):
            core = Core(
                False,
                cost_management_client=Mock(),
            )
            assert core.subscription_id == "env-sub-id-456"

    def test_get_subscription_id_raises_error_when_not_found(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Subscription name is required"):
                Core(
                    False,
                    cost_management_client=Mock(),
                )

    def test_get_subscription_id_not_found_by_name(self):
        mock_subscription = Mock()
        mock_subscription.display_name = "other-subscription"
        mock_subscription.subscription_id = "other-sub-id"

        mock_subscription_client = Mock()
        mock_subscription_client.subscriptions.list.return_value = [mock_subscription]

        with pytest.raises(ValueError, match="Subscription 'non-existent-subscription' not found"):
            Core(
                False,
                subscription_name="non-existent-subscription",
                cost_management_client=Mock(),
                subscription_client=mock_subscription_client,
            )


class TestCoreGetUsage:
    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_get_usage_monthly(self):
        mock_col1 = Mock()
        mock_col1.name = "BillingMonth"
        mock_col2 = Mock()
        mock_col2.name = "Cost"
        mock_usage_total = Mock()
        mock_usage_total.columns = [mock_col1, mock_col2]
        mock_usage_total.rows = [
            ["2023-08-01T00:00:00", 492.77],
            ["2023-09-01T00:00:00", 80.28],
        ]

        mock_col3 = Mock()
        mock_col3.name = "BillingMonth"
        mock_col4 = Mock()
        mock_col4.name = "Cost"
        mock_col5 = Mock()
        mock_col5.name = "ServiceName"
        mock_usage_dimensions = Mock()
        mock_usage_dimensions.columns = [mock_col3, mock_col4, mock_col5]
        mock_usage_dimensions.rows = [
            ["2023-08-01T00:00:00", 492.77, "Cognitive Services"],
            ["2023-09-01T00:00:00", 80.28, "Cognitive Services"],
        ]

        mock_client = Mock()
        mock_client.query.usage.side_effect = [mock_usage_total, mock_usage_dimensions]

        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            cost_management_client=mock_client,
        )

        total_results, results = core.get_usage(ago=1)

        assert len(total_results) == 2
        assert total_results[0]["BillingMonth"] == "2023-08-01T00:00:00"
        assert total_results[0]["Cost"] == 492.77
        assert len(results) == 2
        assert results[0]["ServiceName"] == "Cognitive Services"

        # Verify API was called correctly
        assert mock_client.query.usage.call_count == 2

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_get_usage_daily(self):
        mock_col1 = Mock()
        mock_col1.name = "UsageDate"
        mock_col2 = Mock()
        mock_col2.name = "Cost"
        mock_usage_total = Mock()
        mock_usage_total.columns = [mock_col1, mock_col2]
        mock_usage_total.rows = [
            ["20230901", 10.5],
        ]

        mock_col3 = Mock()
        mock_col3.name = "UsageDate"
        mock_col4 = Mock()
        mock_col4.name = "Cost"
        mock_col5 = Mock()
        mock_col5.name = "ServiceName"
        mock_usage_dimensions = Mock()
        mock_usage_dimensions.columns = [mock_col3, mock_col4, mock_col5]
        mock_usage_dimensions.rows = [
            ["20230901", 10.5, "Storage"],
        ]

        mock_client = Mock()
        mock_client.query.usage.side_effect = [mock_usage_total, mock_usage_dimensions]

        core = Core(
            False,
            granularity="DAILY",
            dimensions=["ServiceName"],
            cost_management_client=mock_client,
        )

        total_results, results = core.get_usage(ago=1)

        assert len(total_results) == 1
        assert total_results[0]["UsageDate"] == "20230901"
        assert len(results) == 1
        assert results[0]["ServiceName"] == "Storage"

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_get_usage_with_resource_group(self):
        mock_col1 = Mock()
        mock_col1.name = "BillingMonth"
        mock_col2 = Mock()
        mock_col2.name = "Cost"
        mock_usage_total = Mock()
        mock_usage_total.columns = [mock_col1, mock_col2]
        mock_usage_total.rows = [
            ["2023-08-01T00:00:00", 100.0],
        ]

        mock_col3 = Mock()
        mock_col3.name = "BillingMonth"
        mock_col4 = Mock()
        mock_col4.name = "Cost"
        mock_col5 = Mock()
        mock_col5.name = "ServiceName"
        mock_usage_dimensions = Mock()
        mock_usage_dimensions.columns = [mock_col3, mock_col4, mock_col5]
        mock_usage_dimensions.rows = [
            ["2023-08-01T00:00:00", 100.0, "Storage"],
        ]

        mock_client = Mock()
        mock_client.query.usage.side_effect = [mock_usage_total, mock_usage_dimensions]

        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ServiceName"],
            resource_group="test-rg",
            cost_management_client=mock_client,
        )

        total_results, results = core.get_usage(ago=1)

        # Verify scope includes resource group
        calls = mock_client.query.usage.call_args_list
        assert "/resourceGroups/test-rg" in str(calls[0])

    @patch.dict(os.environ, {"AZURE_SUBSCRIPTION_ID": "test-sub-id"})
    def test_get_usage_multiple_dimensions(self):
        mock_col1 = Mock()
        mock_col1.name = "BillingMonth"
        mock_col2 = Mock()
        mock_col2.name = "Cost"
        mock_usage_total = Mock()
        mock_usage_total.columns = [mock_col1, mock_col2]
        mock_usage_total.rows = [
            ["2023-08-01T00:00:00", 492.77],
        ]

        mock_col3 = Mock()
        mock_col3.name = "BillingMonth"
        mock_col4 = Mock()
        mock_col4.name = "Cost"
        mock_col5 = Mock()
        mock_col5.name = "ResourceGroup"
        mock_col6 = Mock()
        mock_col6.name = "ServiceName"
        mock_usage_dimensions = Mock()
        mock_usage_dimensions.columns = [mock_col3, mock_col4, mock_col5, mock_col6]
        mock_usage_dimensions.rows = [
            ["2023-08-01T00:00:00", 281.0, "RG-1", "Cognitive Services"],
            ["2023-08-01T00:00:00", 211.77, "RG-2", "Cognitive Services"],
        ]

        mock_client = Mock()
        mock_client.query.usage.side_effect = [mock_usage_total, mock_usage_dimensions]

        core = Core(
            False,
            granularity="MONTHLY",
            dimensions=["ResourceGroup", "ServiceName"],
            cost_management_client=mock_client,
        )

        total_results, results = core.get_usage(ago=1)

        assert len(results) == 2
        assert results[0]["ResourceGroup"] == "RG-1"
        assert results[0]["ServiceName"] == "Cognitive Services"
