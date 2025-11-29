# Apache Airflow Setup for Smart Access Pipeline

## Quick Start

### 1. Start Airflow

```bash
# From project root
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d
```

This starts:
- Airflow Webserver (UI): http://localhost:8080
- Airflow Scheduler (background)
- PostgreSQL database for Airflow metadata (port 5433)

### 2. Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### 3. Run the Pipeline

**Option A: Manual Trigger**
1. Navigate to the `smart_access_pipeline` DAG
2. Click the "Play" button to trigger manually

**Option B: Scheduled Run**
- The DAG runs automatically daily at 2 AM UTC
- View schedule in the DAG details page

### 4. Monitor Execution

- **Graph View**: Visual representation of task dependencies
- **Grid View**: Historical runs and task status
- **Logs**: Click on any task to view detailed execution logs

## Pipeline Tasks

The DAG executes these tasks in sequence:

1. **generate_synthetic_data**: Creates CSV files with IoT device data
2. **load_to_postgres**: Loads raw data into PostgreSQL tables
3. **dbt_run**: Builds staging and mart models (views)
4. **dbt_test**: Runs data quality tests (18 tests)
5. **pipeline_complete**: Success notification

## Configuration

### Change Schedule

Edit `airflow/dags/smart_access_pipeline_dag.py`:

```python
schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
```

Common schedules:
- `'@hourly'` - Every hour
- `'0 */6 * * *'` - Every 6 hours
- `'@daily'` - Daily at midnight
- `'0 8 * * 1'` - Weekly on Mondays at 8 AM

### Modify Retry Logic

In `default_args`:

```python
'retries': 2,                        # Number of retries on failure
'retry_delay': timedelta(minutes=5), # Wait time between retries
```

## Stopping Airflow

```bash
# Stop all services
docker-compose -f docker-compose.airflow.yml down

# Stop and remove volumes (clean slate)
docker-compose -f docker-compose.airflow.yml down -v
```

## Troubleshooting

### DAG Not Appearing

- Check file is in `airflow/dags/` directory
- View Airflow logs: `docker-compose -f docker-compose.airflow.yml logs airflow-scheduler`
- Ensure no Python syntax errors in DAG file

### Task Failures

1. Click on failed task in UI
2. View logs for error details
3. Common issues:
   - PostgreSQL connection (ensure main DB is running on localhost:5432)
   - Path issues (check `PROJECT_ROOT` in DAG file)
   - Permission errors (check file permissions)

### Performance

- Default setup uses LocalExecutor (1 task at a time)
- For parallel execution, switch to CeleryExecutor or KubernetesExecutor

## Production Considerations

For production deployments:

1. **Use secrets management**: Store DB credentials in Airflow Connections/Variables
2. **Enable authentication**: Configure proper user management
3. **Set up monitoring**: Integrate with Prometheus/Grafana
4. **Scale workers**: Use CeleryExecutor with Redis
5. **Backup metadata DB**: Regular backups of Airflow PostgreSQL
