#!/bin/bash
set -e

alembic upgrade head
exec python -m app.runners.admin 