#!/bin/bash
set -e
THIS_DIR=$(dirname "$0")
cd "$THIS_DIR"
uv pip compile base.in -o base.txt --upgrade --python-version 3.14
uv pip compile production.in -o production.txt --upgrade --python-version 3.14
uv pip compile local.in -o local.txt --upgrade --python-version 3.14
