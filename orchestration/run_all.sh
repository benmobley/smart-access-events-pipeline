#!/usr/bin/env bash
set -euo pipefail

# Go to project root (this script lives in orchestration/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

cd "$PROJECT_ROOT"

echo "[orchestration] Activating venv..."
source "$PROJECT_ROOT/venv/bin/activate"

echo "[orchestration] Generating synthetic data..."
python "$PROJECT_ROOT/etl/generate_synthetic_data.py"

echo "[orchestration] Loading data into Postgres..."
python "$PROJECT_ROOT/etl/load_to_postgres.py"

echo "[orchestration] Running dbt models..."
cd "$PROJECT_ROOT/smart_access_dbt"
dbt run

echo "[orchestration] Running dbt tests..."
dbt test

echo "[orchestration] Pipeline completed successfully ✅"