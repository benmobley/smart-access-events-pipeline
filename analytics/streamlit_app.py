"""
Smart Access Events Pipeline - Streamlit Dashboard

Connect to the local Postgres DB `smart_access` and visualize:
  - High-level KPIs (total events, failure rate, avg online_ratio)
  - Filters for date range, region, device_model
  - Line chart: daily opens/closes/failures over time
  - Bar chart: failure rate by device_model and firmware_version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# ==================== Configuration ====================

st.set_page_config(
    page_title="Smart Access Events Dashboard",
    page_icon="🚪",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/smart_access"

# ==================== Database Connection ====================

@st.cache_resource
def get_database_engine():
    """Create and cache database connection engine."""
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=300)
def load_daily_summary():
    """Load device daily summary data."""
    engine = get_database_engine()
    query = """
    SELECT 
        dds.*,
        dd.device_type,
        dd.model,
        dd.firmware_version,
        dh.region
    FROM fct_device_daily_summary dds
    JOIN dim_device dd ON dds.device_id = dd.device_id
    JOIN dim_household dh ON dd.household_id = dh.household_id
    ORDER BY dds.date DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_access_events():
    """Load access events data with dimensions."""
    engine = get_database_engine()
    query = """
    SELECT 
        fae.*,
        dd.device_type,
        dd.model,
        dd.firmware_version,
        dh.region
    FROM fct_access_events fae
    JOIN dim_device dd ON fae.device_id = dd.device_id
    JOIN dim_household dh ON dd.household_id = dh.household_id
    """
    return pd.read_sql(query, engine)

# ==================== Data Loading ====================

try:
    df_daily = load_daily_summary()
    df_events = load_access_events()
    
    # Convert date columns
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_events['event_ts'] = pd.to_datetime(df_events['event_ts'])
    df_events['event_date'] = df_events['event_ts'].dt.date
    
except Exception as e:
    st.error(f"❌ Error connecting to database: {e}")
    st.info("Make sure PostgreSQL is running and dbt models have been executed.")
    st.stop()

# ==================== Sidebar Filters ====================

st.sidebar.header("🔍 Filters")

# Date range filter
min_date = df_daily['date'].min().date()
max_date = df_daily['date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Region filter
regions = ['All'] + sorted(df_daily['region'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# Device model filter
models = ['All'] + sorted(df_daily['model'].unique().tolist())
selected_model = st.sidebar.selectbox("Device Model", models)

# Device type filter
device_types = ['All'] + sorted(df_daily['device_type'].unique().tolist())
selected_device_type = st.sidebar.selectbox("Device Type", device_types)

# ==================== Apply Filters ====================

# Filter daily summary
df_filtered = df_daily[
    (df_daily['date'].dt.date >= start_date) & 
    (df_daily['date'].dt.date <= end_date)
]

if selected_region != 'All':
    df_filtered = df_filtered[df_filtered['region'] == selected_region]

if selected_model != 'All':
    df_filtered = df_filtered[df_filtered['model'] == selected_model]

if selected_device_type != 'All':
    df_filtered = df_filtered[df_filtered['device_type'] == selected_device_type]

# Filter events
df_events_filtered = df_events[
    (df_events['event_date'] >= start_date) & 
    (df_events['event_date'] <= end_date)
]

if selected_region != 'All':
    df_events_filtered = df_events_filtered[df_events_filtered['region'] == selected_region]

if selected_model != 'All':
    df_events_filtered = df_events_filtered[df_events_filtered['model'] == selected_model]

if selected_device_type != 'All':
    df_events_filtered = df_events_filtered[df_events_filtered['device_type'] == selected_device_type]

# ==================== Main Dashboard ====================

st.title("🚪 Smart Access Events Dashboard")
st.markdown("Real-time analytics for IoT smart garage doors and gates")

# ==================== KPI Metrics ====================

st.header("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_events = df_filtered['total_events'].sum()
total_failures = df_filtered['failures'].sum()
failure_rate = (total_failures / total_events * 100) if total_events > 0 else 0
avg_online_ratio = df_filtered['online_ratio'].mean() * 100 if df_filtered['online_ratio'].notna().any() else 0
avg_battery = df_filtered['avg_battery_pct'].mean() if df_filtered['avg_battery_pct'].notna().any() else 0

col1.metric(
    "Total Events",
    f"{total_events:,}",
    delta=None
)

col2.metric(
    "Failure Rate",
    f"{failure_rate:.2f}%",
    delta=f"{total_failures:,} failures",
    delta_color="inverse"
)

col3.metric(
    "Avg Online Ratio",
    f"{avg_online_ratio:.1f}%",
    delta=None
)

col4.metric(
    "Avg Battery Level",
    f"{avg_battery:.1f}%",
    delta=None
)

st.divider()

# ==================== Time Series Analysis ====================

st.header("📈 Daily Event Trends")

# Aggregate by date
daily_trends = df_filtered.groupby('date').agg({
    'opens': 'sum',
    'closes': 'sum',
    'failures': 'sum',
    'total_events': 'sum'
}).reset_index()

# Create line chart
fig_trends = go.Figure()

fig_trends.add_trace(go.Scatter(
    x=daily_trends['date'],
    y=daily_trends['opens'],
    name='Opens',
    mode='lines+markers',
    line=dict(color='#2ecc71', width=2)
))

fig_trends.add_trace(go.Scatter(
    x=daily_trends['date'],
    y=daily_trends['closes'],
    name='Closes',
    mode='lines+markers',
    line=dict(color='#3498db', width=2)
))

fig_trends.add_trace(go.Scatter(
    x=daily_trends['date'],
    y=daily_trends['failures'],
    name='Failures',
    mode='lines+markers',
    line=dict(color='#e74c3c', width=2)
))

fig_trends.update_layout(
    title="Daily Opens, Closes, and Failures Over Time",
    xaxis_title="Date",
    yaxis_title="Count",
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig_trends, use_container_width=True)

st.divider()

# ==================== Failure Analysis ====================

st.header("⚠️ Failure Rate Analysis")

col1, col2 = st.columns(2)

# Failure rate by model
with col1:
    model_failures = df_filtered.groupby('model').agg({
        'failures': 'sum',
        'total_events': 'sum'
    }).reset_index()
    model_failures['failure_rate'] = (model_failures['failures'] / model_failures['total_events'] * 100)
    
    fig_model = px.bar(
        model_failures,
        x='model',
        y='failure_rate',
        title="Failure Rate by Device Model",
        labels={'failure_rate': 'Failure Rate (%)', 'model': 'Device Model'},
        color='failure_rate',
        color_continuous_scale='Reds'
    )
    fig_model.update_layout(height=400)
    st.plotly_chart(fig_model, use_container_width=True)

# Failure rate by firmware version
with col2:
    firmware_failures = df_filtered.groupby('firmware_version').agg({
        'failures': 'sum',
        'total_events': 'sum'
    }).reset_index()
    firmware_failures['failure_rate'] = (firmware_failures['failures'] / firmware_failures['total_events'] * 100)
    
    fig_firmware = px.bar(
        firmware_failures,
        x='firmware_version',
        y='failure_rate',
        title="Failure Rate by Firmware Version",
        labels={'failure_rate': 'Failure Rate (%)', 'firmware_version': 'Firmware Version'},
        color='failure_rate',
        color_continuous_scale='Reds'
    )
    fig_firmware.update_layout(height=400)
    st.plotly_chart(fig_firmware, use_container_width=True)

st.divider()

# ==================== Device Health Metrics ====================

st.header("🔋 Device Health Metrics")

col1, col2 = st.columns(2)

# Battery levels by device type
with col1:
    battery_by_type = df_filtered.groupby('device_type')['avg_battery_pct'].mean().reset_index()
    battery_by_type = battery_by_type.dropna()
    
    if not battery_by_type.empty:
        fig_battery = px.bar(
            battery_by_type,
            x='device_type',
            y='avg_battery_pct',
            title="Average Battery Level by Device Type",
            labels={'avg_battery_pct': 'Battery Level (%)', 'device_type': 'Device Type'},
            color='avg_battery_pct',
            color_continuous_scale='Greens'
        )
        fig_battery.update_layout(height=400)
        st.plotly_chart(fig_battery, use_container_width=True)
    else:
        st.info("No battery data available for the selected filters.")

# Signal strength distribution
with col2:
    signal_data = df_filtered[df_filtered['avg_signal_strength_dbm'].notna()]
    
    if not signal_data.empty:
        fig_signal = px.histogram(
            signal_data,
            x='avg_signal_strength_dbm',
            title="Signal Strength Distribution",
            labels={'avg_signal_strength_dbm': 'Signal Strength (dBm)'},
            nbins=30,
            color_discrete_sequence=['#9b59b6']
        )
        fig_signal.update_layout(height=400)
        st.plotly_chart(fig_signal, use_container_width=True)
    else:
        st.info("No signal strength data available for the selected filters.")

st.divider()

# ==================== Event Type Distribution ====================

st.header("🎯 Event Type Distribution")

event_counts = df_events_filtered['event_type'].value_counts().reset_index()
event_counts.columns = ['event_type', 'count']

col1, col2 = st.columns([1, 1])

with col1:
    fig_pie = px.pie(
        event_counts,
        values='count',
        names='event_type',
        title="Event Type Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Trigger source distribution
    trigger_counts = df_events_filtered['trigger_source'].value_counts().reset_index()
    trigger_counts.columns = ['trigger_source', 'count']
    
    fig_trigger = px.pie(
        trigger_counts,
        values='count',
        names='trigger_source',
        title="Trigger Source Breakdown",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_trigger, use_container_width=True)

st.divider()

# ==================== Data Tables ====================

st.header("📋 Detailed Data")

tab1, tab2 = st.tabs(["Daily Summary", "Recent Events"])

with tab1:
    st.subheader("Device Daily Summary")
    display_cols = ['date', 'device_id', 'device_type', 'model', 'total_events', 
                    'opens', 'closes', 'failures', 'avg_battery_pct', 'online_ratio']
    st.dataframe(
        df_filtered[display_cols].sort_values('date', ascending=False).head(100),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("Recent Access Events")
    event_cols = ['event_ts', 'event_id', 'device_id', 'device_type', 'model', 
                  'event_type', 'trigger_source', 'region']
    st.dataframe(
        df_events_filtered[event_cols].sort_values('event_ts', ascending=False).head(100),
        use_container_width=True,
        hide_index=True
    )

# ==================== Footer ====================

st.divider()
st.caption("📊 Smart Access Events Pipeline | Data refreshes every 5 minutes")