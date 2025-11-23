# Smart Access Events Pipeline

An end-to-end data engineering project simulating IoT telemetry from smart garage door and gate devices. This pipeline demonstrates best practices in modern analytics engineering: synthetic data generation, ETL processing, dimensional modeling with dbt, and interactive analytics.

**Inspired by**: Chamberlain Group's myQ smart access ecosystem

---

## 📋 Overview

This project models a realistic IoT scenario where smart garage doors and gates generate access events (opens, closes, failures) along with device health metrics. The pipeline:

1. **Generates** synthetic IoT event data for 1,000+ households and 3,000+ devices
2. **Extracts & Loads** raw data into PostgreSQL (data warehouse)
3. **Transforms** data using dbt into staging models and analytics-ready marts
4. **Visualizes** insights through a Streamlit dashboard

The architecture follows the **ELT pattern** (Extract-Load-Transform) with a focus on SQL-based transformations and dimensional modeling.

---

## 🛠️ Tech Stack

| Layer               | Technology             | Purpose                               |
| ------------------- | ---------------------- | ------------------------------------- |
| **Data Generation** | Python (pandas, numpy) | Synthetic IoT event generation        |
| **Data Warehouse**  | PostgreSQL             | Raw data storage and query engine     |
| **Transformation**  | dbt (data build tool)  | SQL-based data modeling & testing     |
| **Orchestration**   | Python scripts         | ETL pipeline execution                |
| **Analytics**       | Streamlit              | Interactive dashboard & visualization |
| **Environment**     | Python venv            | Dependency management                 |

---

## 📊 Data Model

### **Architecture**: Kimball Dimensional Model (Star Schema)

#### **Staging Layer** (`models/staging/`)

Raw data cleaned and standardized:

- `stg_access_events` - IoT access events (opens, closes, failures)
- `stg_devices` - Device registry (type, model, firmware)
- `stg_households` - Household metadata (region, timezone)
- `stg_device_health` - Device telemetry (battery, signal strength, online status)

#### **Marts Layer** (`models/marts/`)

**Dimension Tables:**

- `dim_device` - Device attributes (type, model, firmware version, installation date)
- `dim_household` - Household attributes (region, timezone)

**Fact Tables:**

- `fct_access_events` - Granular access events with device/household context
  - Grain: One row per access event
  - Measures: event_type, trigger_source, location (lat/lon)
- `fct_device_daily_summary` - Daily device performance metrics
  - Grain: One row per device per day
  - Measures: total_events, opens, closes, failures, avg_battery_pct, signal_strength, online_ratio

---

## 🚀 How to Run

### **Prerequisites**

- Python 3.9+
- PostgreSQL installed and running
- Git

### **1. Setup Environment**

```bash
# Clone the repository
git clone <your-repo-url>
cd smart-access-events-pipeline

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Generate Synthetic Data**

```bash
# Generate households, devices, and access events
python etl/generate_synthetic_data.py

# Data will be saved to data/raw/
# - households/households.csv (1,000 households)
# - devices/devices.csv (3,000 devices)
# - access_events/access_events.csv (~210,000 events for 7 days)
```

### **3. Load Data to PostgreSQL**

```bash
# Create database and load raw data
python etl/load_to_postgres.py

# This creates:
# - Database: smart_access
# - Schema: public
# - Tables: raw_households, raw_devices, raw_access_events
```

### **4. Run dbt Transformations**

```bash
cd smart_access_dbt

# Install dbt dependencies (if any)
dbt deps

# Run models (staging + marts)
dbt run

# Run data quality tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve  # Opens in browser at http://localhost:8080
```

### **5. Launch Streamlit Dashboard**

```bash
# From project root
streamlit run analytics/streamlit_app.py

# Dashboard opens at http://localhost:8501
```

---

## 📈 Example Analytics Questions

The dashboard and data model enable answering questions like:

### **Operational Analytics**

- What is the daily failure rate across all devices?
- Which device models have the highest command failure rates?
- How does firmware version impact device reliability?
- What's the average battery level and signal strength by device type?

### **User Behavior**

- What are peak usage hours for garage door operations?
- How frequently do users open/close doors via app vs. keypad vs. schedule?
- Which regions show the highest device activity?

### **Device Health Monitoring**

- Which devices have degraded battery levels or poor connectivity?
- What's the correlation between signal strength and command failures?
- How does online/offline status vary by time of day?

### **Capacity Planning**

- What's the daily event volume trend over the past week?
- Which households have the most devices installed?
- Are there devices that haven't reported events recently?

---

## 📁 Project Structure

```
smart-access-events-pipeline/
├── data/
│   └── raw/                    # Generated CSV files
│       ├── access_events/
│       ├── devices/
│       └── households/
├── etl/
│   ├── generate_synthetic_data.py  # Data generation script
│   └── load_to_postgres.py         # ETL to warehouse
├── smart_access_dbt/
│   ├── models/
│   │   ├── staging/            # Cleaned raw tables
│   │   └── marts/              # Dimensions & facts
│   ├── tests/                  # dbt data tests
│   └── dbt_project.yml         # dbt configuration
├── analytics/
│   └── streamlit_app.py        # Dashboard application
└── README.md
```

---

## 🧪 Data Quality & Testing

The project includes dbt tests to ensure data integrity:

- **Uniqueness**: `event_id` in `stg_access_events` is unique
- **Not Null**: Critical foreign keys validated
- **Referential Integrity**: Device/household relationships verified
- **Accepted Values**: Event types constrained to `['open', 'close', 'command_failed']`

Run tests: `dbt test`

---

## 🔮 Future Enhancements

- [ ] Add Airflow for orchestration scheduling
- [ ] Implement incremental models for event data
- [ ] Add real-time streaming with Kafka
- [ ] Create dbt snapshots for slowly changing dimensions
- [ ] Expand dashboard with predictive maintenance alerts
- [ ] Add geospatial analysis for device locations

---

## 📝 License

This is a learning project for portfolio demonstration purposes.

---

## 🙋 Questions or Feedback?

Feel free to open an issue or reach out with suggestions!
