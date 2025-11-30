"""
Smart Access Streaming Pipeline - Airflow DAG

Orchestrates periodic transformations and maintenance for the streaming pipeline.
While Kafka handles continuous data ingestion, this DAG runs:
- Incremental dbt transformations every 15 minutes
- Data quality tests
- Monitoring and alerting
"""

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Project paths
PROJECT_ROOT = Path("/opt/airflow")
DBT_DIR = PROJECT_ROOT / "smart_access_dbt"

# Default arguments
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'execution_timeout': timedelta(minutes=10),
}

# DAG for incremental transformations
dag = DAG(
    'smart_access_streaming_pipeline',
    default_args=default_args,
    description='Incremental transformations for streaming data pipeline',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=['iot', 'streaming', 'dbt', 'kafka'],
)

# Task 1: Run incremental dbt models
dbt_run_incremental = BashOperator(
    task_id='dbt_run_incremental',
    bash_command=f'cd {DBT_DIR} && dbt run --profiles-dir {DBT_DIR}',
    dag=dag,
)

# Task 2: Run dbt tests
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command=f'cd {DBT_DIR} && dbt test --profiles-dir {DBT_DIR}',
    dag=dag,
)

# Task 3: Log completion
pipeline_complete = BashOperator(
    task_id='transformation_complete',
    bash_command='echo "Incremental transformation completed at $(date)"',
    dag=dag,
)

# Define task dependencies
dbt_run_incremental >> dbt_test >> pipeline_complete
