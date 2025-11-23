# Smart Access Events Pipeline

End-to-end IoT analytics pipeline simulating smart garage door/gate telemetry. Demonstrates synthetic data generation, Python ETL, PostgreSQL warehousing, dbt transformations, and Streamlit visualization.

**Inspired by**: Chamberlain Group's myQ smart access ecosystem

---

## 🚀 Quick Start - Complete Pipeline

Run the full pipeline from data generation to dashboard in 5 steps:

### **Prerequisites**

- Python 3.9+
- PostgreSQL running locally
- Git

### **Step 1: Environment Setup**

```bash
git clone <your-repo-url>
cd smart-access-events-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 2: Generate Synthetic Data**

```bash
python etl/generate_synthetic_data.py
# Creates: 1,000 households, 3,000 devices, ~210K events (7 days)
```

### **Step 3: Load to PostgreSQL**

```bash
python etl/load_to_postgres.py
# Creates database 'smart_access' with raw tables
```

### **Step 4: Run dbt Models**

```bash
cd smart_access_dbt
dbt run    # Build staging + mart views in smart_access schema
dbt test   # Validate data quality
cd ..
```

### **Step 5: Launch Dashboard**

```bash
streamlit run analytics/streamlit_app.py
# Opens at http://localhost:8501
```

---

## 📊 Data Architecture

**Pipeline Flow**: Synthetic Data → PostgreSQL (Raw Tables) → dbt (Views in `smart_access` schema) → Streamlit

### **Raw Layer** (`public` schema)

- `raw_access_events` - Raw event data
- `raw_devices` - Raw device data
- `raw_households` - Raw household data
- `raw_device_health` - Raw device health metrics

### **Staging Layer** (`smart_access` schema - Views)

- `stg_access_events` - Cleaned event log (opens/closes/failures)
- `stg_devices` - Cleaned device registry (type, model, firmware)
- `stg_households` - Cleaned household metadata (region, timezone)
- `stg_device_health` - Cleaned device telemetry (battery, signal, connectivity)

### **Marts Layer** (`smart_access` schema - Star Schema Views)

**Dimensions:**

- `dim_device` - Device attributes joined with household context
- `dim_household` - Household attributes with region and timezone

**Facts:**

- `fct_access_events` - Event-level grain with surrogate keys
- `fct_device_daily_summary` - Daily aggregations (opens, closes, failures, battery, signal strength, online ratio)

---

## 🛠️ Tech Stack

**Data Generation & ETL**: Python · Faker · pandas · SQLAlchemy  
**Database**: PostgreSQL (with separate schemas for raw and transformed data)  
**Transformation**: dbt Core (materializing models as views)  
**Visualization**: Streamlit · Plotly

---

## 📈 Dashboard Features

The Streamlit dashboard provides:

- **KPI Metrics**: Total events, failure rate, online ratio, battery levels
- **Interactive Filters**: Date range, region, device model, device type
- **Visualizations**:
  - Time series: Daily opens/closes/failures
  - Failure analysis by model and firmware version
  - Device health: Battery and signal strength
  - Event distribution: Type breakdown and trigger sources
- **Data Tables**: Recent events and daily summaries

---

## 💡 Example Analytics

**Operational**: Which device models have highest failure rates?  
**User Behavior**: What are peak usage hours for garage operations?  
**Device Health**: Which devices need battery replacement or have poor connectivity?  
**Capacity**: What's the event volume trend over the past week?

---

## 📁 Project Structure

```
smart-access-events-pipeline/
├── data/raw/                       # Generated CSV files
│   ├── access_events/
│   ├── devices/
│   ├── households/
│   └── device_health/
├── etl/
│   ├── generate_synthetic_data.py  # Synthetic data generator
│   └── load_to_postgres.py         # Loads CSVs to PostgreSQL raw tables
├── smart_access_dbt/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/                # Cleaned source data (views)
│       │   └── smart_access/
│       └── marts/                  # Analytics models (views)
│           └── smart_access/
├── analytics/
│   └── streamlit_app.py            # Interactive dashboard
└── requirements.txt                # Python dependencies
```

---

## 🧪 Data Quality

dbt tests validate:

- **Uniqueness**: Primary keys (event_id, device_key, household_key)
- **Not null constraints**: Critical fields across all models
- **Referential integrity**: Foreign key relationships between facts and dimensions
- **Accepted values**: Event types restricted to valid values (open, close, command_failed)

Run: `dbt test` (18 tests included)

---

## 🔮 Future Enhancements

- **Orchestration**: Airflow/Dagster for scheduled pipeline runs
- **Materialization**: Convert views to tables for better performance at scale
- **Incremental Models**: Process only new/changed data
- **Streaming**: Real-time ingestion with Kafka
- **SCD Type 2**: Track dimension changes over time with dbt snapshots
- **ML**: Predictive maintenance based on device health patterns
- **Advanced Analytics**: Geospatial analysis, user behavior clustering

---

**Portfolio Project** | Built to demonstrate modern data engineering practices
