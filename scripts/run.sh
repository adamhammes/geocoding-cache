#!/bin/bash
set -euo pipefail

. .env
./venv/bin/python -m flask run
