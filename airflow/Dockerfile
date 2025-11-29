FROM apache/airflow:2.8.0-python3.11

# Install project dependencies
USER airflow
RUN pip install --no-cache-dir \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    psycopg2-binary>=2.9.9 \
    sqlalchemy>=2.0.0 \
    dbt-core>=1.7.0 \
    dbt-postgres>=1.7.0 \
    faker>=20.0.0
