# Smart Access Events Pipeline

End-to-end IoT analytics pipeline simulating smart garage door telemetry with **real-time streaming** (Kafka) and **batch processing** (Airflow). Built with dbt transformations and Streamlit visualization.

**Inspired by**: Chamberlain Group's myQ ecosystem

---

## 🚀 Quick Start

**Prerequisites**: Python 3.9+ · PostgreSQL · Docker

### **Streaming Workflow** (Real-Time)

```bash
# 1. Setup environment
git clone https://github.com/benmobley/smart-access-events-pipeline.git
cd smart-access-events-pipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Create database and load initial schema
createdb smart_access
python etl/generate_synthetic_data.py
python etl/load_to_postgres.py

# 3. Start Kafka
docker-compose -f docker-compose.kafka.yml up -d

# 4. Run streaming pipeline (2 terminals)
python streaming/kafka_consumer.py    # Terminal 1: Consumes from Kafka → PostgreSQL
python streaming/kafka_producer.py    # Terminal 2: Generates events → Kafka

# 5. Transform and visualize
cd smart_access_dbt && dbt run && cd ..
streamlit run analytics/streamlit_app.py
```

**Access**: Dashboard http://localhost:8501 | Kafka UI http://localhost:8090

📖 **[Full Streaming Guide →](streaming/README.md)**

---

### **Batch Workflow** (Scheduled)

**Option 1: Airflow** (runs daily at 2 AM UTC)

```bash
docker-compose -f docker-compose.airflow.yml --env-file .env.airflow up -d
# Airflow UI: http://localhost:8080 (airflow/airflow)
```

**Option 2: Manual Bash Script**

```bash
./orchestration/run_all.sh
streamlit run analytics/streamlit_app.py
```

---

## 📊 Architecture

### **Data Flow**

**Streaming**: IoT Simulator → Kafka Topics → Consumer → PostgreSQL → dbt (incremental) → Dashboard  
**Batch**: Synthetic Generator → CSV Files → PostgreSQL → dbt (full refresh) → Dashboard

### **Data Models** (Star Schema)

**Raw** (`public` schema): Landing tables for events, devices, households, health metrics

**Staging** (`smart_access` schema): Cleaned, standardized views

**Marts** (`smart_access` schema):

- **Dimensions**: `dim_device`, `dim_household`
- **Facts**: `fct_access_events` (event-level), `fct_device_daily_summary` (aggregated)

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
