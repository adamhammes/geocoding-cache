#!/bin/sh
set -euo pipefail

. .env
python -m flask run
