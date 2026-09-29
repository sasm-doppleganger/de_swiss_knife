#!/bin/sh

set -e

echo "==> Running CI"

echo "==> Running tests"
npm test

echo "==> Running lint"
npm run lint

echo "==> CI passed!"
