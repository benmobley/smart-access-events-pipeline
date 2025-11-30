# Smart Access Events Pipeline

End-to-end IoT analytics pipeline simulating smart garage door/gate telemetry. Features **real-time streaming** (Kafka) and **batch processing** (Airflow) architectures with dbt transformations and Streamlit visualization.

**Inspired by**: Chamberlain Group's myQ smart access ecosystem

---

## 🚀 Quick Start

**Prerequisites**: Python 3.9+ · PostgreSQL · Docker

### **Real-Time Streaming** (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/benmobley/smart-access-events-pipeline.git
cd smart-access-events-pipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start Kafka infrastructure
docker-compose -f docker-compose.kafka.yml up -d

# 3. Run producer & consumer (separate terminals)
python streaming/kafka_consumer.py
python streaming/kafka_producer.py

# 4. Transform and visualize
cd smart_access_dbt && dbt run && cd ..
streamlit run analytics/streamlit_app.py
```

**Access**: Dashboard at http://localhost:8501 | Kafka UI at http://localhost:8090

📖 **[Streaming Setup Guide →](streaming/README.md)**

---

### **Batch Processing**

**Option 1: Airflow** (scheduled daily at 2 AM UTC)
```bash
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d
# UI: http://localhost:8080 (airflow/airflow)
```

**Option 2: Bash Script**
```bash
./orchestration/run_all.sh
streamlit run analytics/streamlit_app.py
```

---

## 📊 Architecture

**Streaming**: Kafka Producer → Kafka Broker → Consumer → PostgreSQL → dbt → Streamlit  
**Batch**: Synthetic Generator → CSV → PostgreSQL → dbt → Streamlit

### **Data Models** (Dimensional - Star Schema)

**Raw Layer** (`public` schema): `raw_access_events`, `raw_devices`, `raw_households`, `raw_device_health`

**Staging** (`smart_access` schema): Cleaned views with standardized naming and data types

**Marts** (`smart_access` schema):
- **Dimensions**: `dim_device`, `dim_household` (slowly changing over time)
- **Facts**: `fct_access_events` (event grain), `fct_device_daily_summary` (aggregated metrics)

---

## 🛠️ Tech Stack

**Streaming**: Kafka · Zookeeper · kafka-python  
**Orchestration**: Airflow · Docker Compose  
**ETL**: Python · Faker · pandas · SQLAlchemy  
**Database**: PostgreSQL  
**Transformation**: dbt Core  
**Visualization**: Streamlit · Plotly

---

## 📈 Analytics Capabilities

**Metrics**: Event volumes, failure rates, device health (battery/signal), online ratios  
**Visualizations**: Time series trends, failure analysis by model/firmware, health monitoring  
**Filtering**: Date ranges, regions, device types/models  
**Use Cases**: Predictive maintenance, operational monitoring, user behavior analysis

---

## 📁 Project Structure

```
├── streaming/           # Kafka producer/consumer, real-time ingestion
├── airflow/dags/        # Batch (daily) and streaming (15min) DAGs
├── etl/                 # Synthetic data generation and CSV loading
├── smart_access_dbt/    # dbt models (staging + marts)
├── analytics/           # Streamlit dashboard
├── orchestration/       # Bash automation script
└── docker-compose.*     # Kafka and Airflow infrastructure
```

---

## 🧪 Data Quality

18 dbt tests validate uniqueness, not-null constraints, referential integrity, and accepted values.

---

## 🔮 Roadmap

- ✅ Kafka real-time streaming
- 🔄 Incremental dbt models for streaming data
- 🔄 SCD Type 2 for dimension history tracking
- 🔄 Predictive maintenance ML models
- 🔄 Data quality monitoring (Great Expectations)

---

**Portfolio Project** | Modern data engineering with streaming and batch architectures
