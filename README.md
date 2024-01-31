# azurecost

[![PyPI version](https://badge.fury.io/py/azurecost.svg)](https://badge.fury.io/py/azurecost)
[![Build Status](https://github.com/toyama0919/azurecost/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/toyama0919/azurecost/actions/workflows/ci.yml)

Simple and easy command line to view azure costs.

Support python3 only.

## Settings

```sh
az login
```

## Examples

#### show cost monthly

```bash
$ azurecost -s my-subscription
key                   2023-08    2023-09
------------------  ---------  ---------
total                  492.77      80.28
Cognitive Services     492.77      80.28
Bandwidth                0          0
Storage                  0          0
```

* You can omit the -s by specifying the environment variable AZURE_SUBSCRIPTION_ID.

#### show cost (Multiple Dimensions)

```
$ azurecost -s my-subscription -d ResourceGroup -d ServiceName
key                                     2023-08    2023-09
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

## Python API

```py
subscription = "my-subscription"
core = Azurecost(
    False,
    "MONTHLY",
    ["ServiceName"],
    subscription_name=subscription,
    # resource_group="my-rg"
)
total_results, results = core.get_usage(
    ago=2,
)
text = core.convert_tabulate(total_results, results)
print(text)
```

## Installation

```sh
pip install azurecost
```

## CI

### install test package

```
$ ./scripts/ci.sh install
```

### test

```
$ ./scripts/ci.sh run-test
```

flake8 and black and pytest.

### release pypi

```
$ ./scripts/ci.sh release
```

git tag and pypi release.
