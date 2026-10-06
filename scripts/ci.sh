#!/bin/bash -e

install-test() {
  pip3 install ".[test]"
}

run-test() {
  tox -e black
  tox -e flake8
  tox -e pytest
}

$@
