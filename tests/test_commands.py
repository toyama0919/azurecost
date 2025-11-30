import pytest
from unittest.mock import Mock, patch
from azurecost import commands
from azurecost import constants
from click.testing import CliRunner


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_show_version(runner):
    result = runner.invoke(commands.cli, ["-v"])
    assert result.exit_code == 0
    assert result.output.strip() == constants.VERSION


@patch("azurecost.commands.Core")
def test_cli_basic_usage(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = (
        [{"BillingMonth": "2023-08-01T00:00:00", "Cost": 492.77}],
        [
            {
                "BillingMonth": "2023-08-01T00:00:00",
                "Cost": 492.77,
                "ServiceName": "Cognitive Services",
                "Currency": "USD",
            }
        ],
    )
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(commands.cli, ["-s", "test-subscription"])
    assert result.exit_code == 0
    assert "test output" in result.output
    mock_core.get_usage.assert_called_once_with(1)


@patch("azurecost.commands.Core")
def test_cli_with_debug(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = ([], [])
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(commands.cli, ["-s", "test-subscription", "--debug"])
    assert result.exit_code == 0
    mock_core_class.assert_called_once()
    # Check that debug=True was passed as first positional argument
    call_args = mock_core_class.call_args
    assert call_args[0][0] is True  # debug parameter


@patch("azurecost.commands.Core")
def test_cli_with_resource_group(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = ([], [])
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(
        commands.cli, ["-s", "test-subscription", "-r", "test-rg"]
    )
    assert result.exit_code == 0
    call_args = mock_core_class.call_args
    # Core(debug, granularity, dimensions, subscription, resource_group)
    assert call_args[0][4] == "test-rg"  # resource_group is 5th positional arg


@patch("azurecost.commands.Core")
def test_cli_with_dimensions(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = ([], [])
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(
        commands.cli,
        ["-s", "test-subscription", "-d", "ResourceGroup", "-d", "ServiceName"],
    )
    assert result.exit_code == 0
    call_args = mock_core_class.call_args
    # Core(debug, granularity, dimensions, subscription, resource_group)
    dimensions = call_args[0][2]  # dimensions is 3rd positional arg
    assert "ResourceGroup" in dimensions
    assert "ServiceName" in dimensions


@patch("azurecost.commands.Core")
def test_cli_with_granularity(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = ([], [])
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(commands.cli, ["-s", "test-subscription", "-g", "DAILY"])
    assert result.exit_code == 0
    call_args = mock_core_class.call_args
    # Core(debug, granularity, dimensions, subscription, resource_group)
    assert call_args[0][1] == "DAILY"  # granularity is 2nd positional arg


@patch("azurecost.commands.Core")
def test_cli_with_ago(mock_core_class, runner):
    mock_core = Mock()
    mock_core.get_usage.return_value = ([], [])
    mock_core.convert_tabulate.return_value = "test output"
    mock_core_class.return_value = mock_core

    result = runner.invoke(commands.cli, ["-s", "test-subscription", "-a", "3"])
    assert result.exit_code == 0
    mock_core.get_usage.assert_called_once_with(3)


@patch("azurecost.commands.Core")
def test_cli_without_subscription_raises_error(mock_core_class, runner):
    # Simulate Core raising ValueError when subscription is not found
    mock_core_class.side_effect = ValueError("Subscription name is required.")
    result = runner.invoke(commands.cli, [])
    assert result.exit_code != 0
