#!/bin/sh
set -euxo pipefail

. .env
python -m flask run
