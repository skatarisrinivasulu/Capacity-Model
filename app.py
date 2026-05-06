import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Capacity Model", layout="wide")

st.title("🏭 Capacity Analysis Model")
# st.markdown("Based on your exact logic — Cyclic/Non-Cyclic, HC constraints, auto-calculations")

# --- Data Input ---
st.subheader("1. Enter Your Data")

uploaded_file = st.file_uploader("Upload your data (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

    def normalize_column_name(name):
        return str(name).strip().lower().replace('.', '').replace('-', '_').replace(' ', '_')

    df.columns = [normalize_column_name(col) for col in df.columns]
    column_renames = {
        'cycle_no': 'Cycle_No',
        'cycle no': 'Cycle_No',
        'cycleno': 'Cycle_No',
        'task_type': 'Task_Type',
        'task type': 'Task_Type',
        'resource_type': 'Resource_Type',
        'resource type': 'Resource_Type',
        'min_hc_required': 'Min_HC_Required',
        'min hc required': 'Min_HC_Required',
        'frequency_per_cycle': 'Frequency_per_cycle',
        'frequency per cycle': 'Frequency_per_cycle',
        'frequencypercycle': 'Frequency_per_cycle',
        'start': 'Start',
        'end': 'End',
        'date': 'Date',
        'line': 'Line',
        'station': 'Station',
        'task': 'Task',
        'shop': 'Shop',
        'Shop': 'Shop'
    }
    df = df.rename(columns={k: v for k, v in column_renames.items() if k in df.columns})

    if 'Station' in df.columns:
        df['Station'] = df['Station'].astype(str)

    if 'Shop' in df.columns:
        df['Shop'] = df['Shop'].astype(str)

    if 'Frequency_per_cycle' not in df.columns:
        df['Frequency_per_cycle'] = 1
        st.warning('Missing Frequency per cycle column: defaulting to 1 for all rows.')
else:
    # Sample data
    sample_data = [
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Weld Frame", "Resource_Type": "PA1", "Min_HC_Required": 2, "Start": "13:00:00", "End": "13:01:00", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Weld Frame", "Resource_Type": "PA2", "Min_HC_Required": 2, "Start": "13:00:00", "End": "13:01:30", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:01:30", "End": "13:01:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S2", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:01:30", "End": "13:01:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-002", "Task_Type": "Cyclic", "Task": "Weld Frame", "Resource_Type": "PA1", "Min_HC_Required": 2, "Start": "13:00:00", "End": "13:01:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-002", "Task_Type": "Cyclic", "Task": "Weld Frame", "Resource_Type": "PA2", "Min_HC_Required": 2, "Start": "13:00:00", "End": "13:01:30", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-002", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:01:30", "End": "13:02:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S2", "Date": "2026-04-27", "Cycle_No": "CYC-002", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:02:30", "End": "13:03:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line A", "Station": "S2", "Date": "2026-04-27", "Cycle_No": "CYC-003", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA1", "Min_HC_Required": 1, "Start": "13:01:30", "End": "13:02:45", "Frequency_per_cycle": 1},
         {"Shop": "Shop A", "Line": "Line A", "Station": "S2", "Date": "2026-04-27", "Cycle_No": "CYC-003", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:01:30", "End": "13:02:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop A", "Line": "Line B", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:02:30", "End": "13:03:45", "Frequency_per_cycle": 1},
        {"Shop": "Shop B", "Line": "Line C", "Station": "S1", "Date": "2026-04-27", "Cycle_No": "CYC-001", "Task_Type": "Cyclic", "Task": "Assemble", "Resource_Type": "PA2", "Min_HC_Required": 1, "Start": "13:02:30", "End": "13:04:00", "Frequency_per_cycle": 1},
        {("Shop"):("Shop A"), ("Line"):("Line A"), ("Station"):("S1"), ("Date"):("2026-04-27"), ("Cycle_No"):("CYC-001"), ("Task_Type"):("Non-Cyclic"), ("Task"):("Calibrate Machine"), ("Resource_Type"):("Machine1"), ("Min_HC_Required"):(0), ("Start"):("13:01:45"), ("End"):("13:02:30"), ("Frequency_per_cycle"): (0.25)}
    ]
    df = pd.DataFrame(sample_data)

# Convert timestamps
df['Start'] = pd.to_datetime(df['Start'], format='%H:%M:%S')
df['End'] = pd.to_datetime(df['End'], format='%H:%M:%S')


# Ensure Date is string
df['Date'] = df['Date'].astype(str)

# Add datetime columns
df['Start_dt'] = pd.to_datetime(df['Date'] + ' ' + df['Start'].dt.strftime('%H:%M:%S'))
df['End_dt'] = pd.to_datetime(df['Date'] + ' ' + df['End'].dt.strftime('%H:%M:%S'))

df['Duration'] = (df['End_dt'] - df['Start_dt']).dt.total_seconds()
df['Weighted_Duration'] = df['Duration'] * df['Frequency_per_cycle']

# --- Step 1: Compute Actual HC (PA-only) per Cycle per Station ---
# Create boolean mask for PA resources
pa_pattern = r'^PA\d+$'  # Matches PA1, PA2, PA10, etc.
df['Is_PA'] = df['Resource_Type'].astype(str).str.match(pa_pattern, na=False)

# Count unique PA resource types per (Shop, Line, Station, Cycle_No)
df['Actual_HC'] = df.groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
)['Resource_Type'].transform(
    lambda x: x[df['Is_PA']].nunique()  # Only count PA resources
)

# Ensure integer and fill NaN
df['Actual_HC'] = df['Actual_HC'].fillna(0).astype(int)

# # --- 7. PA Usage Summary (by Shop, Line, Station, Cycle) ---
# st.subheader("📊 PA Usage Summary (by Shop, Line, Station, Cycle)")

# Group by Shop, Line, Station, Cycle_No and use the pre-computed Actual_HC
pa_summary = df.groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
).agg(
    Actual_HC=('Actual_HC', 'first')  # Use the computed unique count
)

# Ensure integer and fill NaN (shouldn't happen, but safe)
pa_summary['Actual_HC'] = pa_summary['Actual_HC'].fillna(0).astype(int)

# Sort by Shop, Line, Station, Cycle_No for readability
pa_summary = pa_summary.sort_values(
    ['Shop', 'Line', 'Station', 'Cycle_No']
)

# # Display as clean, readable table
# st.dataframe(
#     pa_summary.style.format({
#         'Actual_HC': '{:.0f}'  # No decimals
#     }).set_table_styles([
#         {
#             'selector': 'th',
#             'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
#         }
#     ])
# )


# Group by Shop, Line, Station, Cycle_No
grouped = df.groupby(['Shop', 'Line', 'Station', 'Cycle_No'], as_index=False).agg({
    'Start_dt': 'min',
    'End_dt': 'max'
})

grouped['Total_Cycle_Time'] = (grouped['End_dt'] - grouped['Start_dt']).dt.total_seconds()



# # --- 8. Non-Cyclic Cycles by Shop, Line, Station, and PA_Used ---
# st.subheader("📊 Non-Cyclic Cycles by Shop, Line, Station, and PA Used")

# Step 1: Identify cycles with Non-Cyclic tasks
non_cyclic_cycles = df[df['Task_Type'] == 'Non-Cyclic'][['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']].drop_duplicates()

# Step 2: Attach Actual_HC to each cycle
cycle_hc = df[['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']].drop_duplicates()

# Step 3: Merge Non-Cyclic cycles with HC info
non_cyclic_with_hc = non_cyclic_cycles.merge(
    cycle_hc,
    on=['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC'],
    how='left'
)

# Step 4: Group by Shop, Line, Station, Actual_HC and count non-cyclic cycles
result = non_cyclic_with_hc.groupby(
    ['Shop', 'Line', 'Station', 'Actual_HC'],
    as_index=False
).size().reset_index().rename(columns={0: 'Non_Cyclic_Cycles'})

# Sort for readability
result = result.sort_values(['Shop', 'Line', 'Station', 'Actual_HC'])

# # Display as clean table
# st.dataframe(
#     result.style.format({
#         'Actual_HC': '{:.0f}',
#         'Non_Cyclic_Cycles': '{:.0f}'
#     }).set_table_styles([
#         {
#             'selector': 'th',
#             'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
#         }
#     ])
# )



# # --- 9. Cycle Time Metrics by Shop, Line, Station, Cycle, and PA_Used (Actual_HC) ---
# st.subheader("📊 Cycle Time Metrics by Shop, Line, Station, Cycle, and PA Used (Actual_HC)")

# Step 1: Get cycle time per cycle
cycle_time_data = grouped.groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
).agg(
    Total_Cycle_Time=('Total_Cycle_Time', 'first')
)

# Step 2: Merge with Actual_HC
cycle_with_hc = cycle_time_data.merge(
    df[['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']].drop_duplicates(),
    on=['Shop', 'Line', 'Station', 'Cycle_No'],
    how='left'
)

# Step 3: Compute Non-Cyclic Task Time and Weighted Time
non_cyclic = df[df['Task_Type'] == 'Non-Cyclic'].copy()
non_cyclic['Task_Time'] = (non_cyclic['End_dt'] - non_cyclic['Start_dt']).dt.total_seconds()
non_cyclic['Weighted_Non_Cyclic_Time'] = non_cyclic['Task_Time'] * non_cyclic['Frequency_per_cycle']

# Step 4: Group non-cyclic tasks by cycle
non_cyclic_grouped = non_cyclic[
    non_cyclic['Task_Time'] > 0
].groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
).agg(
    Task_Time=('Task_Time', 'sum'),
    Weighted_Non_Cyclic_Time=('Weighted_Non_Cyclic_Time', 'sum')
)

# Step 5: Merge non-cyclic data with all cycles
per_cycle_summary = cycle_with_hc.merge(
    non_cyclic_grouped,
    on=['Shop', 'Line', 'Station', 'Cycle_No'],
    how='left'
)

# Step 6: Fill missing values (no non-cyclic tasks) with 0
per_cycle_summary['Task_Time'] = per_cycle_summary['Task_Time'].fillna(0)
per_cycle_summary['Weighted_Non_Cyclic_Time'] = per_cycle_summary['Weighted_Non_Cyclic_Time'].fillna(0)

# Step 7: Compute Cyclic Cycle Time per cycle
per_cycle_summary['Cyclic_Cycle_Time'] = (
    per_cycle_summary['Total_Cycle_Time'] - per_cycle_summary['Task_Time']
).clip(lower=0)

# Step 8: Sort
per_cycle_summary = per_cycle_summary.sort_values(
    ['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']
)

# # Display per-cycle table
# st.markdown("#### 📊 Per-Cycle Summary (All Cycles, Including Those Without Non-Cyclic Tasks)")
# st.dataframe(
#     per_cycle_summary.style.format({
#         'Total_Cycle_Time': '{:.2f}',
#         'Cyclic_Cycle_Time': '{:.2f}',
#         'Task_Time': '{:.2f}',
#         'Weighted_Non_Cyclic_Time': '{:.2f}',
#         'Actual_HC': '{:.0f}'
#     }).set_table_styles([
#         {
#             'selector': 'th',
#             'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
#         }
#     ])
# )

# # --- 9. Cycle Time Metrics by Shop, Line, Station, Cycle, and PA_Used (Actual_HC) ---
# st.subheader("📊 Cycle Time Metrics by Shop, Line, Station, Cycle, and PA Used (Actual_HC)")

# Step 1: Get cycle time per cycle
cycle_time_data = grouped.groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
).agg(
    Total_Cycle_Time=('Total_Cycle_Time', 'first')
)

# Step 2: Merge with Actual_HC
cycle_with_hc = cycle_time_data.merge(
    df[['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']].drop_duplicates(),
    on=['Shop', 'Line', 'Station', 'Cycle_No'],
    how='left'
)

# Step 3: Compute Non-Cyclic Task Time and Weighted Time
non_cyclic = df[df['Task_Type'] == 'Non-Cyclic'].copy()
non_cyclic['Task_Time'] = (non_cyclic['End_dt'] - non_cyclic['Start_dt']).dt.total_seconds()
non_cyclic['Weighted_Non_Cyclic_Time'] = non_cyclic['Task_Time'] * non_cyclic['Frequency_per_cycle']

# Step 4: Group non-cyclic tasks by cycle
non_cyclic_grouped = non_cyclic.groupby(
    ['Shop', 'Line', 'Station', 'Cycle_No'],
    as_index=False
).agg(
    Task_Time=('Task_Time', 'sum'),
    Weighted_Non_Cyclic_Time=('Weighted_Non_Cyclic_Time', 'sum')
)

# Step 5: Merge non-cyclic data with all cycles
per_cycle_summary = cycle_with_hc.merge(
    non_cyclic_grouped,
    on=['Shop', 'Line', 'Station', 'Cycle_No'],
    how='left'
)

# Step 6: Fill missing values (no non-cyclic tasks) with 0
per_cycle_summary['Task_Time'] = per_cycle_summary['Task_Time'].fillna(0)
per_cycle_summary['Weighted_Non_Cyclic_Time'] = per_cycle_summary['Weighted_Non_Cyclic_Time'].fillna(0)

# Step 7: Compute Cyclic Cycle Time per cycle
per_cycle_summary['Cyclic_Cycle_Time'] = (
    per_cycle_summary['Total_Cycle_Time'] - per_cycle_summary['Task_Time']
).clip(lower=0)

# Step 8: Sort
per_cycle_summary = per_cycle_summary.sort_values(
    ['Shop', 'Line', 'Station', 'Cycle_No', 'Actual_HC']
)

# # Display per-cycle table
# st.markdown("#### 📊 Per-Cycle Summary (All Cycles, Including Those Without Non-Cyclic Tasks)")
# st.dataframe(
#     per_cycle_summary.style.format({
#         'Total_Cycle_Time': '{:.2f}',
#         'Cyclic_Cycle_Time': '{:.2f}',
#         'Task_Time': '{:.2f}',
#         'Weighted_Non_Cyclic_Time': '{:.2f}',
#         'Actual_HC': '{:.0f}'
#     }).set_table_styles([
#         {
#             'selector': 'th',
#             'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
#         }
#     ])
# )

# Step 9: Aggregate per (Shop, Line, Station, Actual_HC)
aggregated_summary = per_cycle_summary.groupby(
    ['Shop', 'Line', 'Station', 'Actual_HC'],
    as_index=False
).agg(
    Total_Cycles=('Cycle_No', 'nunique'),
    Total_Cyclic_Time=('Cyclic_Cycle_Time', 'sum'),
    Total_Weighted_Non_Cyclic_Time=('Weighted_Non_Cyclic_Time', 'sum'),
    Total_Non_Cyclic_Cycles=('Task_Time', lambda x: (x > 0).sum())
)

# Step 10: Compute Averages
aggregated_summary['Avg_Cyclic_Cycle_Time'] = (
    aggregated_summary['Total_Cyclic_Time'] / aggregated_summary['Total_Cycles']
).round(2)

# ✅ Fix: Set Avg_Weighted_Non_Cyclic_Time_Per_Cycle = 0 if Total_Non_Cyclic_Cycles = 0
aggregated_summary['Avg_Weighted_Non_Cyclic_Time_Per_Cycle'] = (
    aggregated_summary['Total_Weighted_Non_Cyclic_Time'] / aggregated_summary['Total_Non_Cyclic_Cycles']
).where(
    aggregated_summary['Total_Non_Cyclic_Cycles'] > 0,
    0.0
).round(2)

aggregated_summary['Avg_Cycle_Time'] = (
    aggregated_summary['Avg_Cyclic_Cycle_Time'] + aggregated_summary['Avg_Weighted_Non_Cyclic_Time_Per_Cycle']
).round(2)

aggregated_summary['Throughput_(units/hour)'] = (
    3600 / aggregated_summary['Avg_Cycle_Time']
).round(2)

# Round all numeric columns
aggregated_summary = aggregated_summary.round(2)

# Sort
aggregated_summary = aggregated_summary.sort_values(['Shop', 'Line', 'Station', 'Actual_HC'])

# # Display aggregated summary
# st.markdown("#### 📊 Aggregated Averages (by Shop, Line, Station, PA_Used)")
# st.dataframe(
#     aggregated_summary.style.format({
#         'Total_Cycles': '{:.0f}',
#         'Total_Cyclic_Time': '{:.2f}',
#         'Total_Weighted_Non_Cyclic_Time': '{:.2f}',
#         'Total_Non_Cyclic_Cycles': '{:.0f}',
#         'Avg_Cyclic_Cycle_Time': '{:.2f}',
#         'Avg_Weighted_Non_Cyclic_Time_Per_Cycle': '{:.2f}',
#         'Avg_Cycle_Time': '{:.2f}',
#         'Throughput_(units/hour)': '{:.2f}'
#     }).set_table_styles([
#         {
#             'selector': 'th',
#             'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
#         }
#     ])
# )



# --- 6. Target Cycle Time Calculation (User Inputs) ---
st.subheader("🎯 Target Cycle Time Calculation")

with st.expander("🔧 Configure Production Targets & Constraints", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        weekly_target = st.number_input(
            "📅 Weekly Production Target (units/week)",
            min_value=1,
            value=1000,
            step=100,
            help="How many units do you plan to build per week?"
        )

    with col2:
        working_hours_per_week = st.number_input(
            "⏰ Working Hours per Week",
            min_value=1,
            value=40,
            step=1,
            help="Total available working hours per week (e.g., 40 for full-time)"
        )

    with col3:
        oee = st.number_input(
            "🏭 OEE (Overall Equipment Effectiveness)",
            min_value=0.0,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Enter OEE as a decimal (e.g., 0.85 for 85%)"
        )

# --- Calculate Target Cycle Time ---
available_seconds_per_week = working_hours_per_week * 3600 * oee
target_cycle_time_sec = available_seconds_per_week / weekly_target


# --- Display Target Cycle Time ---
st.markdown("### 🎯 Calculated Target Cycle Time")
st.metric(
    label="🎯 Target Cycle Time (sec)",
    value=f"{target_cycle_time_sec:.2f} sec",
)



# --- 10. Bottleneck Analysis: Identify Bottlenecks & Optimal HC ---
st.subheader("🚨 Bottleneck Analysis: Target vs. Actual Cycle Time")

# Ensure target_cycle_time_sec is float
target_cycle_time_sec = float(target_cycle_time_sec)

# Step 1: Get best performance per (Shop, Line, Station) — use aggregated_summary
# Group by Shop, Line, Station and find the row with min Avg_Cycle_Time
best_performance_per_station = aggregated_summary.groupby(
    ['Shop', 'Line', 'Station'],
    as_index=False
).apply(
    lambda x: x.loc[x['Avg_Cycle_Time'].idxmin()]
).reset_index(drop=True)

# ✅ Force a fresh copy to avoid view issues
best_performance_per_station = best_performance_per_station.copy()

# ✅ Add Is_Bottleneck column
best_performance_per_station['Is_Bottleneck'] = (
    best_performance_per_station['Avg_Cycle_Time'] > target_cycle_time_sec
)

# ✅ Add target and difference
best_performance_per_station['Target_Cycle_Time'] = target_cycle_time_sec
best_performance_per_station['Cycle_Time_Difference'] = (
    best_performance_per_station['Avg_Cycle_Time'] - target_cycle_time_sec
).round(2)

# ✅ Define columns to display
display_cols = [
    'Shop', 'Line', 'Station',
    'Actual_HC',
    'Avg_Cycle_Time',
    'Target_Cycle_Time',
    'Cycle_Time_Difference',
    'Is_Bottleneck'
]

# ✅ Reorder and sort
best_performance_per_station = best_performance_per_station[display_cols].sort_values(
    ['Is_Bottleneck', 'Avg_Cycle_Time'],
    ascending=[False, True]
)

# ✅ Display the result
st.markdown("#### 📊 Bottleneck Summary (Per Shop, Line, Station)")
st.dataframe(best_performance_per_station)

# --- Optional: Show detailed breakdown per station ---
with st.expander("🔍 View Detailed Performance by HC Level (Per Station)", expanded=False):
    # ✅ Ensure target_cycle_time_sec is float
    target_cycle_time_sec = float(target_cycle_time_sec)

    for idx, row in best_performance_per_station.iterrows():
        shop, line, station = row['Shop'], row['Line'], row['Station']
        
        # Filter aggregated_summary for this station
        subset = aggregated_summary[
            (aggregated_summary['Shop'] == shop) &
            (aggregated_summary['Line'] == line) &
            (aggregated_summary['Station'] == station)
        ].copy()
        
        # ✅ Check if any data exists
        if subset.empty:
            st.warning(f"No data found for {shop} | {line} | {station}")
            continue

        # ✅ Verify required columns exist
        required_cols = ['Actual_HC', 'Avg_Cyclic_Cycle_Time', 'Avg_Weighted_Non_Cyclic_Time_Per_Cycle', 'Avg_Cycle_Time', 'Throughput_(units/hour)']
        missing_cols = [col for col in required_cols if col not in subset.columns]
        if missing_cols:
            st.error(f"Missing columns in aggregated_summary: {missing_cols}")
            continue

        # ✅ Sort by Avg_Cycle_Time (best first)
        subset = subset.sort_values('Avg_Cycle_Time')

        # ✅ Select only desired columns
        display_cols = [
            'Actual_HC',
            'Avg_Cyclic_Cycle_Time',
            'Avg_Weighted_Non_Cyclic_Time_Per_Cycle',
            'Avg_Cycle_Time',
            'Throughput_(units/hour)'
        ]

        # ✅ Format only the selected columns
        styled_subset = subset[display_cols].style.format({
            'Actual_HC': '{:.0f}',
            'Avg_Cyclic_Cycle_Time': '{:.2f}',
            'Avg_Weighted_Non_Cyclic_Time_Per_Cycle': '{:.2f}',
            'Avg_Cycle_Time': '{:.2f}',
            'Throughput_(units/hour)': '{:.2f}'
        }).set_table_styles([
            {
                'selector': 'th',
                'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
            }
        ])

        # ✅ Display
        st.markdown(f"**📊 {shop} | {line} | {station}**")
        st.dataframe(styled_subset)


# --- Tabs: One Tab per Shop (Using Best Performance Data) ---
st.subheader("5. Shop Selection (Click to View)")

# Use best_performance_per_station as the source
# It already contains: Shop, Line, Station, Actual_HC, Avg_Cycle_Time, Is_Bottleneck, etc.
# We'll recompute needed metrics if needed

# Get unique shops
shops = best_performance_per_station['Shop'].unique()

# Create tabs
tab_names = [f"🏢 {shop}" for shop in shops]
tabs = st.tabs(tab_names)

# --- Loop over shops and lines ---
for tab, shop in zip(tabs, shops):
    with tab:
        # Filter data for this shop
        shop_data = best_performance_per_station[best_performance_per_station['Shop'] == shop]
        lines = shop_data['Line'].unique()

        # Create sub-tabs for each line
        line_tab_names = [f"🔧 {line}" for line in lines]
        line_tabs = st.tabs(line_tab_names)

        for line_tab, line in zip(line_tabs, lines):
            with line_tab:
                # Filter data for this line
                line_data = shop_data[shop_data['Line'] == line]
                stations = line_data['Station'].unique()

                # --- Plotly: Station Cycle Time (Interactive) ---
                st.markdown("#### 📊 Station Cycle Time (Interactive)")

                # Prepare data
                line_station_summary = line_data[['Station', 'Avg_Cycle_Time']].copy()
                labels = line_station_summary['Station'].astype(str).tolist()
                cycle_times_sec = line_station_summary['Avg_Cycle_Time'].tolist()

                # Convert seconds to mm:ss format
                def seconds_to_mmss_with_mins(seconds):
                    m, s = divmod(int(seconds), 60)
                    return f"{m}:{s:02d} mins"

                cycle_times_mmss = [seconds_to_mmss_with_mins(t) for t in cycle_times_sec]

                # ✅ Get target cycle time (already defined earlier)
                target_cycle_time_sec = float(target_cycle_time_sec)  # Ensure it's float

                # Determine status for each station
                statuses = []
                colors = []
                for station, cycle_time in zip(labels, cycle_times_sec):
                    if cycle_time > target_cycle_time_sec:
                        status = "⚠️ Bottleneck"
                        color = "red"
                    else:
                        status = "✅ Normal"
                        color = "skyblue"
                    statuses.append(status)
                    colors.append(color)

                # Create customdata for hover
                customdata = []
                for station, cycle_time, status in zip(labels, cycle_times_sec, statuses):
                    customdata.append([station, cycle_time, status])

                # Create figure
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=labels,
                    y=cycle_times_sec,
                    name='Avg Cycle Time (sec)',
                    marker_color=colors,
                    text=cycle_times_mmss,
                    textposition='outside',
                    textfont=dict(size=10, color='black'),
                    hovertemplate=
                        "<b>Station: %{x}</b><br>" +
                        "Cycle Time: %{text}<br>" +
                        "Status: <b>%{customdata[2]}</b><br>" +
                        "<extra></extra>",
                    customdata=customdata
                ))

                fig.update_layout(
                    xaxis=dict(title=dict(text="Station", font=dict(size=12))),
                    yaxis=dict(
                        title=dict(text="Avg Cycle Time (seconds)", font=dict(size=12)),
                        tickfont=dict(size=10),
                        hoverformat='.1f'
                    ),
                    hovermode="x unified",
                    margin=dict(l=50, r=50, t=50, b=50),
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True, key=f"cycle_time_{shop}_{line}")


                # --- Resource Utilization (Per Station) ---
                st.markdown("#### 📊 Resource Utilization (Per Station)")

                # Get all tasks for this line
                line_tasks = df[
                    (df['Shop'] == shop) & 
                    (df['Line'] == line)
                ].copy()

                # Group by Station, Resource_Type, Cycle_No
                resource_util = line_tasks.groupby(
                    ['Station', 'Resource_Type', 'Cycle_No'],
                    as_index=False
                ).agg(
                    Weighted_Duration=('Weighted_Duration', 'sum')
                )

                # Average Weighted Duration per resource per station
                resource_avg = resource_util.groupby(
                    ['Station', 'Resource_Type'],
                    as_index=False
                )['Weighted_Duration'].mean()

                # ✅ Compute bottleneck avg cycle time = max Avg_Cycle_Time in this line
                line_station_summary = line_data[['Station', 'Avg_Cycle_Time']].copy()
                bottleneck_avg_cycle_time = line_station_summary['Avg_Cycle_Time'].max()

                # ✅ Compute utilization: avg duration / bottleneck cycle time
                resource_avg['Utilization (%)'] = (
                    resource_avg['Weighted_Duration'] / bottleneck_avg_cycle_time
                ) * 100

                # ✅ Round to 2 decimals
                resource_avg['Utilization (%)'] = resource_avg['Utilization (%)'].round(2)

                # ✅ Display table
                st.dataframe(
                    resource_avg[['Station', 'Resource_Type', 'Utilization (%)']].style.format({
                        'Utilization (%)': '{:.1f}%'
                    }).set_table_styles([
                        {
                            'selector': 'th',
                            'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]
                        }
                    ])
                )

                # --- Plotly: Resource Utilization (Grouped Bar Chart) ---
                st.markdown("#### 📊 Resource Utilization (%) by Station and Resource Type")

                # Clean and prepare data
                resource_avg_clean = resource_avg.drop_duplicates(subset=['Station', 'Resource_Type'])
                resource_avg_clean = resource_avg_clean.dropna(subset=['Station', 'Resource_Type'])

                # Pivot to wide format
                pivot_df = resource_avg_clean.pivot(
                    index='Station',
                    columns='Resource_Type',
                    values='Utilization (%)'
                ).reset_index()

                # Sort by Station
                pivot_df = pivot_df.sort_values('Station')

                # Create figure
                fig = go.Figure()

                # Add bars for each resource type
                for i, resource_type in enumerate(pivot_df.columns[1:]):
                    fig.add_trace(go.Bar(
                        x=pivot_df['Station'],
                        y=pivot_df[resource_type],
                        name=resource_type,
                        marker_color=px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)],
                        text=[f"{v:.1f}%" if pd.notna(v) and v > 0 else "" for v in pivot_df[resource_type]],
                        textposition='outside',
                        textfont=dict(size=10, color='black'),
                        hovertemplate=
                            "<b>Station: %{x}</b><br>" +
                            f"{resource_type}: <b>%{{y:.1f}}%</b><br>" +
                            "<extra></extra>",
                        customdata=[bottleneck_avg_cycle_time] * len(pivot_df)  # Pass bottleneck time to hover
                    ))

                # ✅ Update layout with better formatting
                fig.update_layout(
                    title=dict(
                        text="Resource Utilization (%)",
                        x=0.5,
                        xanchor="center",
                        font=dict(size=16)
                    ),
                    xaxis=dict(
                        title=dict(text="Station", font=dict(size=12))
                    ),
                    yaxis=dict(
                        title=dict(text="Utilization (%)", font=dict(size=12)),
                        tickfont=dict(size=10),
                        range=[0, 1.2 * pivot_df.iloc[:, 1:].max().max()]
                    ),
                    barmode='group',
                    hovermode="x unified",
                    margin=dict(l=50, r=50, t=80, b=50),
                    height=500,
                    legend=dict(
                        x=0.95,
                        y=1,
                        xanchor="right",
                        yanchor="top",
                        font=dict(size=10)
                    )
                )

                # ✅ Add a note below the chart
                st.markdown(f"ℹ️ **Bottleneck Cycle Time (Max in Line): {bottleneck_avg_cycle_time:.2f} sec**")

                # ✅ Display chart
                st.plotly_chart(fig, use_container_width=True, key=f"utilization_{shop}_{line}")

                # --- Task Time (With Frequency) ---
                st.markdown("#### 📈 Task Time (With Frequency) per Station")

                # Add task time
                line_tasks['Task_Time'] = (line_tasks['End_dt'] - line_tasks['Start_dt']).dt.total_seconds()
                line_tasks['Weighted_Task_Time'] = line_tasks['Task_Time'] * line_tasks['Frequency_per_cycle']

                # Group by Station, Task
                task_summary = line_tasks.groupby(['Station', 'Task'], as_index=False).agg(
                    Avg_Task_Time=('Task_Time', 'mean'),
                    Avg_Weighted_Task_Time=('Weighted_Task_Time', 'mean'),
                    Resources_Used=('Resource_Type', lambda x: ', '.join(x.unique()))
                )

                task_summary['Avg_Task_Time'] = task_summary['Avg_Task_Time'].round(2)
                task_summary['Avg_Weighted_Task_Time'] = task_summary['Avg_Weighted_Task_Time'].round(2)

                st.dataframe(
                    task_summary[['Station', 'Task', 'Avg_Task_Time', 'Avg_Weighted_Task_Time', 'Resources_Used']]
                )