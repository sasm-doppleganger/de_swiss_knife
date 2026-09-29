#!/bin/bash

set -e

echo "==> Running Python CI"

echo "==> Checking Python"
python --version

echo "==> Installing dependencies"
pip install -r requirements.txt

echo "==> Running Python"
python main.py

echo "==> CI passed!"