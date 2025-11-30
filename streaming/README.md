# Kafka Streaming Setup Guide

## Overview

The streaming architecture enables real-time ingestion of IoT device events using Apache Kafka. Events are continuously produced, consumed, and written to PostgreSQL, with Airflow orchestrating periodic transformations.

---

## Architecture

```
IoT Devices (Simulated) → Kafka Producer → Kafka Broker → Kafka Consumer → PostgreSQL
                                                                              ↓
                                                                          dbt (Airflow)
                                                                              ↓
                                                                          Streamlit
```

**Components:**

- **Kafka Producer** (`streaming/kafka_producer.py`): Simulates real-time device events
- **Kafka Broker**: Message queue for event streaming
- **Kafka Consumer** (`streaming/kafka_consumer.py`): Writes events to PostgreSQL
- **Airflow**: Runs incremental dbt transformations every 15 minutes
- **dbt**: Transforms raw streaming data into analytics models

---

## Quick Start

### 1. Start Kafka Infrastructure

```bash
# Start Kafka, Zookeeper, and Kafka UI
docker-compose -f docker-compose.kafka.yml up -d

# Verify services are running
docker ps --filter "name=kafka"

# Access Kafka UI: http://localhost:8090
```

### 2. Install Streaming Dependencies

```bash
pip install kafka-python>=2.0.2
```

### 3. Start the Consumer (writes to PostgreSQL)

```bash
# In terminal 1
python streaming/kafka_consumer.py
```

### 4. Start the Producer (generates events)

```bash
# In terminal 2
python streaming/kafka_producer.py

# Or run for specific duration
python streaming/kafka_producer.py --duration 10  # 10 minutes
```

### 5. Start Airflow (optional - for scheduled transformations)

```bash
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d

# Access Airflow UI: http://localhost:8080 (airflow/airflow)
# Enable the 'smart_access_streaming_pipeline' DAG
```

### 6. View Dashboard

```bash
streamlit run analytics/streamlit_app.py
# http://localhost:8501
```

---

## Kafka Topics

| Topic                 | Purpose                         | Key         | Value Schema                                                            |
| --------------------- | ------------------------------- | ----------- | ----------------------------------------------------------------------- |
| `smart-access.events` | Access events (open/close/fail) | `device_id` | `{event_id, device_id, event_ts, event_type, trigger_source}`           |
| `smart-access.health` | Device health metrics           | `device_id` | `{device_id, reported_at, battery_pct, signal_strength_dbm, is_online}` |

---

## Configuration

### Producer Settings (`kafka_producer.py`)

```python
NUM_HOUSEHOLDS = 100              # Number of households
NUM_DEVICES_PER_HOUSEHOLD = 3     # Devices per household
EVENT_RATE_PER_DEVICE = 0.1       # Events/sec per device
HEALTH_CHECK_INTERVAL = 30        # Seconds between health reports
```

### Consumer Settings (`kafka_consumer.py`)

```python
BATCH_SIZE = 100        # Messages per batch insert
BATCH_TIMEOUT = 5       # Seconds before forcing batch commit
```

### Airflow DAG

- **Schedule**: Every 15 minutes (`*/15 * * * *`)
- **Tasks**: dbt run (incremental) → dbt test → complete
- **DAG**: `smart_access_streaming_pipeline`

---

## Monitoring

### Kafka UI

**URL**: http://localhost:8090

- View topics, messages, and consumer groups
- Monitor lag and throughput
- Inspect message contents

### Airflow UI

**URL**: http://localhost:8080

- Monitor transformation runs
- View task logs
- Track dbt test results

### PostgreSQL

```bash
# Check row counts
psql -U postgres -d smart_access -c "
SELECT
  (SELECT COUNT(*) FROM raw_access_events) as events,
  (SELECT COUNT(*) FROM raw_device_health) as health;
"
```

---

## Stopping Services

```bash
# Stop Kafka
docker-compose -f docker-compose.kafka.yml down

# Stop Airflow
docker-compose -f docker-compose.airflow.yml down

# Stop producer/consumer: Ctrl+C in their terminals
```

---

## Troubleshooting

### Producer/Consumer Can't Connect

**Issue**: `KafkaError: NoBrokersAvailable`

**Solution**:

```bash
# Ensure Kafka is running
docker ps --filter "name=kafka"

# Check Kafka logs
docker logs kafka --tail 50
```

### Consumer Not Writing to DB

**Issue**: No data appearing in PostgreSQL

**Solution**:

- Check PostgreSQL is running on localhost:5432
- Verify tables exist: `\dt` in psql
- Check consumer logs for errors
- Confirm producer is sending messages (check Kafka UI)

### Airflow DAG Not Running

**Issue**: Streaming DAG not showing up

**Solution**:

- Ensure `smart_access_streaming_dag.py` is in `airflow/dags/`
- Check Airflow scheduler logs: `docker logs airflow-scheduler`
- Manually trigger from UI to test

---

## Performance Tips

**For High Throughput:**

1. Increase consumer batch size:

   ```python
   BATCH_SIZE = 500
   ```

2. Use multiple consumers (Kafka automatically load balances)

3. Partition topics by device_id for parallel processing

4. Use connection pooling for PostgreSQL inserts

**For Low Latency:**

1. Decrease batch timeout:

   ```python
   BATCH_TIMEOUT = 1  # 1 second
   ```

2. Run dbt more frequently:
   ```python
   schedule_interval='*/5 * * * *'  # Every 5 minutes
   ```

---

## Production Considerations

1. **Security**: Enable Kafka authentication (SASL/SSL)
2. **Replication**: Set `replication_factor=3` for topics
3. **Monitoring**: Integrate with Prometheus/Grafana
4. **Alerting**: Set up consumer lag alerts
5. **Backup**: Regular snapshots of Kafka data
6. **Schema Registry**: Use Confluent Schema Registry for schema evolution
7. **Exactly-once semantics**: Enable idempotent producer and transactions

---

## Batch vs Streaming Comparison

| Aspect            | Batch (Original)       | Streaming (New)         |
| ----------------- | ---------------------- | ----------------------- |
| **Data Flow**     | CSV → Load → Transform | Continuous → Transform  |
| **Latency**       | Hours/Daily            | Seconds/Minutes         |
| **Schedule**      | Daily at 2 AM          | Every 15 minutes        |
| **Orchestration** | Airflow full pipeline  | Airflow transforms only |
| **Use Case**      | Historical analysis    | Real-time monitoring    |

---

## Next Steps

- Implement schema registry for data governance
- Add consumer lag monitoring
- Create alerts for pipeline failures
- Implement exactly-once delivery semantics
- Add data quality checks in consumer
