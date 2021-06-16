#!/bin/bash
set -euo pipefail

. .env
python -m flask run
