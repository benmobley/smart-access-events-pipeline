"""
Smart Access Events Pipeline - Airflow DAG

Orchestrates the complete IoT analytics pipeline:
1. Generate synthetic smart access device data
2. Load data into PostgreSQL raw tables
3. Run dbt transformations (staging + marts)
4. Validate data quality with dbt tests

Schedule: Daily at 2 AM UTC
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Project paths (mounted in Docker container)
PROJECT_ROOT = Path("/opt/airflow")
ETL_DIR = PROJECT_ROOT / "etl"
DBT_DIR = PROJECT_ROOT / "smart_access_dbt"

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}

# Define the DAG
dag = DAG(
    'smart_access_pipeline',
    default_args=default_args,
    description='End-to-end smart access IoT analytics pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=['iot', 'analytics', 'dbt', 'smart-access'],
)

# Task 1: Generate synthetic data
generate_data = BashOperator(
    task_id='generate_synthetic_data',
    bash_command=f'python {ETL_DIR}/generate_synthetic_data.py',
    dag=dag,
)

# Task 2: Load data to PostgreSQL
load_to_postgres = BashOperator(
    task_id='load_to_postgres',
    bash_command=f'python {ETL_DIR}/load_to_postgres.py',
    dag=dag,
)

# Task 3: Run dbt models (staging + marts)
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command=f'cd {DBT_DIR} && dbt run --profiles-dir {DBT_DIR}',
    dag=dag,
)

# Task 4: Run dbt tests
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command=f'cd {DBT_DIR} && dbt test --profiles-dir {DBT_DIR}',
    dag=dag,
)

# Task 5: Pipeline success notification (optional)
pipeline_complete = BashOperator(
    task_id='pipeline_complete',
    bash_command='echo "Smart Access Pipeline completed successfully at $(date)"',
    dag=dag,
)

# Define task dependencies (linear flow)
generate_data >> load_to_postgres >> dbt_run >> dbt_test >> pipeline_complete
