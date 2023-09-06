# azurecost

[![PyPI version](https://badge.fury.io/py/azurecost.svg)](https://badge.fury.io/py/azurecost)
[![Build Status](https://github.com/toyama0919/azurecost/actions/workflows/tests.yml/badge.svg?branch=main)(https://github.com/toyama0919/azurecost/actions/workflows/tests.yml)

Simple and easy command line to view azure costs.

Support python3 only. (use boto3)

## Settings

```sh
az login
```

## Examples

#### list instance and cluster

```bash
$ azurecost -s my-subscription                                                                                                   1 ↵
key                   2023-08    2023-09
------------------  ---------  ---------
total                  492.77      80.28
Cognitive Services     492.77      80.28
Bandwidth                0          0
Storage                  0          0
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
