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
dbt deps
dbt run    # Build staging + mart tables
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

**Pipeline Flow**: Synthetic Data → PostgreSQL → dbt → Streamlit

### **Staging Layer**

- `stg_access_events` - Event log (opens/closes/failures)
- `stg_devices` - Device registry (type, model, firmware)
- `stg_households` - Household metadata (region, timezone)
- `stg_device_health` - Device telemetry (battery, signal, connectivity)

### **Marts Layer** (Star Schema)

**Dimensions:**

- `dim_device` - Device attributes
- `dim_household` - Household attributes

**Facts:**

- `fct_access_events` - Event-level grain
- `fct_device_daily_summary` - Daily aggregations (opens, closes, failures, battery, signal strength)

---

## 🛠️ Tech Stack

Python · PostgreSQL · dbt · Streamlit · Plotly · SQLAlchemy · pandas

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
├── etl/
│   ├── generate_synthetic_data.py  # Data generator
│   └── load_to_postgres.py         # Database loader
├── smart_access_dbt/
│   └── models/
│       ├── staging/                # Cleaned source data
│       └── marts/                  # Analytics models
├── analytics/
│   └── streamlit_app.py            # Dashboard
└── requirements.txt                # Python dependencies
```

---

## 🧪 Data Quality

dbt tests validate:

- Uniqueness (event_id primary keys)
- Not null constraints
- Referential integrity
- Accepted values for event types

Run: `dbt test`

---

## 🔮 Future Ideas

- Airflow orchestration · Incremental models · Kafka streaming · dbt snapshots · Predictive maintenance ML · Geospatial analysis

---

**Portfolio Project** | Built to demonstrate modern data engineering practices
