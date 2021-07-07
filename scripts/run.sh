#!/bin/bash
set -euo pipefail

. .env
FLASK_APP=geocoding_cache/server ./venv/bin/python -m flask run
