# azurecost

[![PyPI version](https://badge.fury.io/py/azurecost.svg)](https://badge.fury.io/py/azurecost)
[![Build Status](https://github.com/toyama0919/azurecost/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/toyama0919/azurecost/actions/workflows/ci.yml)

Simple and easy command line tool to view Azure costs.

Supports Python 3.8 and above.

## Installation

```sh
pip install azurecost
```

## Settings

You need to log in with Azure CLI.

```sh
az login
```

You can specify subscription ID and resource group via environment variables.

```sh
export AZURE_SUBSCRIPTION_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export AZURE_RESOURCE_GROUP=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage

### Basic Usage

By default, it displays monthly costs aggregated by service name for the past 1 month.

```bash
$ azurecost -s my-subscription
(JPY)                 2023-08    2023-09
------------------  ---------  ---------
total                  492.77      80.28
Cognitive Services     492.77      80.28
Bandwidth                0          0
Storage                  0          0
```

You can omit the `-s` option if you set the subscription ID via environment variable.

```bash
$ export AZURE_SUBSCRIPTION_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
$ azurecost
(JPY)                 2023-08    2023-09
------------------  ---------  ---------
total                  492.77      80.28
Cognitive Services     492.77      80.28
Bandwidth                0          0
Storage                  0          0
```

**Note:** The currency unit (e.g., `(JPY)`, `(USD)`, `(EUR)`) is automatically determined by your Azure subscription's billing currency settings.

### Multiple Dimensions

You can specify multiple dimensions with the `-d` option.

```bash
$ azurecost -s my-subscription -d ResourceGroup -d ServiceName
(JPY)                                     2023-08    2023-09
------------------------------------  ---------  ---------
total                                    492.77     426.97
RG-1, Cognitive Services                 281        366
RG-2, Cognitive Services                 211.77      60.97
RG-3, Storage                              0          0
RG-4, Storage                              0          0
RG-5, Storage                              0          0
RG-6, Storage                              0          0
RG-7, Bandwidth                            0          0
RG-7, Storage                              0          0
```

### Daily Granularity

Use `-g DAILY` to display daily costs.

```bash
$ azurecost -s my-subscription -g DAILY
```

### Specify Time Period

Use the `-a` option to specify how many periods (months or days) ago to fetch data from.

```bash
# Fetch data from the past 3 months
$ azurecost -s my-subscription -a 3
```

### Filter by Resource Group

Use the `-r` option to filter by a specific resource group.

```bash
$ azurecost -s my-subscription -r my-resource-group
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--subscription` | `-s` | Azure subscription display name. Can be omitted if `AZURE_SUBSCRIPTION_ID` environment variable is set. | `AZURE_SUBSCRIPTION_ID` env var |
| `--resource-group` | `-r` | Filter costs by a specific resource group. Can be omitted if `AZURE_RESOURCE_GROUP` environment variable is set. | `AZURE_RESOURCE_GROUP` env var |
| `--dimensions` | `-d` | Dimensions to aggregate costs by (e.g., ResourceGroup, ServiceName). Can be specified multiple times. | `ServiceName` |
| `--granularity` | `-g` | Time granularity for cost aggregation. Use `MONTHLY` for monthly costs or `DAILY` for daily costs. | `MONTHLY` |
| `--ago` | `-a` | Number of periods (months for MONTHLY, days for DAILY) to look back from today. For example, use 3 to get the past 3 months. | `1` |
| `--debug` | - | Enable debug logging to see detailed request/response information. | `False` |
| `--version` | `-v` | Display the version number and exit. | - |

### Currency Display

The currency unit displayed in the output (e.g., JPY, USD, EUR) is determined by your Azure subscription's billing currency settings. The tool automatically retrieves the currency information from the Azure Cost Management API response and displays it in the output.

**Example output with currency:**
```bash
$ azurecost -s my-subscription
(JPY)                 2023-08    2023-09
------------------  ---------  ---------
total                  492.77      80.28
Cognitive Services     492.77      80.28
```

The currency is shown in the first column header (e.g., `(JPY)`, `(USD)`, `(EUR)`). This currency matches what you see in the Azure Portal's Cost Analysis view for your subscription.

**Note:** The currency cannot be changed via command-line options as it is determined by your Azure billing account settings. If you need to view costs in a different currency, you would need to change the billing currency in your Azure billing account settings.

### Available Dimensions

Examples of dimensions that can be specified with the `-d` option:

- `ResourceGroup` - Resource group
- `ServiceName` - Service name
- `ResourceLocation` - Resource location
- `MeterCategory` - Meter category
- `ResourceType` - Resource type

For other dimensions, refer to the Azure Cost Management API documentation.

## Python API

You can also use it directly from Python code.

```python
from azurecost import Azurecost

# Required parameter
core = Azurecost(
    debug=False,  # Required: Enable debug logging
    # Optional parameters
    granularity="MONTHLY",  # Optional: "MONTHLY" or "DAILY" (default: "MONTHLY")
    dimensions=["ServiceName"],  # Optional: List of dimensions (default: ["ServiceName"])
    subscription_name="my-subscription",  # Optional: Subscription display name (or use AZURE_SUBSCRIPTION_ID env var)
    resource_group="my-rg",  # Optional: Resource group filter (or use AZURE_RESOURCE_GROUP env var)
    # Advanced options (for testing/customization)
    # credential=None,  # Optional: Azure credential object (default: DefaultAzureCredential())
    # cost_management_client=None,  # Optional: CostManagementClient instance (for testing)
    # subscription_client=None,  # Optional: SubscriptionClient instance (for testing)
)

total_results, results = core.get_usage(ago=2)  # ago: number of periods to fetch (default: 1)
text = core.convert_tabulate(total_results, results)
print(text)
```

### Python API Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `debug` | `bool` | Yes | - | Enable debug logging |
| `granularity` | `str` | No | `"MONTHLY"` | Aggregation granularity: `"MONTHLY"` or `"DAILY"` |
| `dimensions` | `list[str]` | No | `["ServiceName"]` | List of dimensions for aggregation |
| `subscription_name` | `str` | No | `None` | Subscription display name (or use `AZURE_SUBSCRIPTION_ID` env var) |
| `resource_group` | `str` | No | `None` | Resource group filter (or use `AZURE_RESOURCE_GROUP` env var) |
| `credential` | `object` | No | `None` | Azure credential object (default: `DefaultAzureCredential()`) |
| `cost_management_client` | `object` | No | `None` | `CostManagementClient` instance (mainly for testing) |
| `subscription_client` | `object` | No | `None` | `SubscriptionClient` instance (mainly for testing) |

## Development

### Setup Test Environment

```bash
$ ./scripts/ci.sh install
```

### Run Tests

```bash
$ ./scripts/ci.sh run-test
```

Runs tests with flake8, black, and pytest.

### Release to PyPI

```bash
$ ./scripts/ci.sh release
```

Creates a git tag and releases to PyPI.
