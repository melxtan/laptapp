import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Patient Data Analysis", layout="wide")

def safe_get_col(df, keys, fill=''):
    for key in keys:
        if key in df.columns:
            return df[key]
    return pd.Series([fill] * len(df), index=df.index)

def group_patient_episodes(df):
    df = df.sort_values(['MRN', 'APPT_DATE']).copy()
    df['Group'] = 0

    prev_mrn = None
    prev_date = None
    group_id = 0

    for idx, row in df.iterrows():
        if (prev_mrn != row['MRN']) or (prev_date is None) or ((row['APPT_DATE'] - prev_date).days > 20):
            group_id += 1
        df.at[idx, 'Group'] = group_id
        prev_mrn = row['MRN']
        prev_date = row['APPT_DATE']

    df['Group Admit Date'] = df.groupby(['MRN', 'Group'])['APPT_DATE'].transform('min')
    df['Group Discharge Date'] = df.groupby(['MRN', 'Group'])['APPT_DATE'].transform('max')
    return df

def process_ip_data(df, selected_date):
    selected_date = pd.to_datetime(selected_date)
    df = df[df['APPT_DATE'] == selected_date]
    df = df.drop_duplicates(subset=['MRN'])
    df = df[['PATIENT', 'MRN', 'MED_SERVICE']]
    df['SOURCE'] = 'IP'
    df['HOME_PHONE'] = ''
    df['EMAIL'] = ''
    return df

def process_new_op_data(df, selected_date):
    df = df[df['PATIENT_CLASS'] != 'Telemedicine'].copy()
    df['APPT_DATE'] = pd.to_datetime(df['APPT_DATE'])
    df = group_patient_episodes(df)
    selected_date = pd.to_datetime(selected_date)
    mask = (df['Group Admit Date'] <= selected_date) & (df['Group Discharge Date'] >= selected_date)
    df = df[mask]
    df = df.drop_duplicates(subset=['MRN', 'Group Admit Date'])
    result_df = pd.DataFrame()
    result_df['PATIENT'] = safe_get_col(df, ['NAME', 'PATIENT', 'PATIENT_NAME'])
    result_df['MRN'] = safe_get_col(df, ['MRN'])
    result_df['MED_SERVICE'] = safe_get_col(df, ['MED_SERVICE', 'SERVICE'])
    result_df['HOME_PHONE'] = safe_get_col(df, ['HOME_PHONE', 'PHONE'])
    result_df['EMAIL'] = safe_get_col(df, ['EMAIL'])
    result_df['SOURCE'] = 'New OP'
    return result_df

def get_historical_data(ip_df, new_op_df, days=30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    ip_df['APPT_DATE'] = pd.to_datetime(ip_df['APPT_DATE'])
    new_op_df['APPT_DATE'] = pd.to_datetime(new_op_df['APPT_DATE'])
    ip_dates = pd.date_range(start=start_date, end=end_date)
    ip_counts = []
    new_op_counts = []
    total_unique_counts = []

    op_grouped = new_op_df[new_op_df['PATIENT_CLASS'] != 'Telemedicine'].copy()
    op_grouped = group_patient_episodes(op_grouped)

    for date in ip_dates:
        # Unique IP MRNs for the date
        ip_mrns = set(ip_df[ip_df['APPT_DATE'].dt.date == date.date()]['MRN'].unique())
        ip_counts.append(len(ip_mrns))

        # Unique New OP MRNs for the date
        mask = (op_grouped['Group Admit Date'] <= date) & (op_grouped['Group Discharge Date'] >= date)
        op_mrns = set(op_grouped[mask].drop_duplicates(subset=['MRN', 'Group Admit Date'])['MRN'])
        new_op_counts.append(len(op_mrns))

        # Total unique MRNs (union)
        total_unique_counts.append(len(ip_mrns.union(op_mrns)))

    return pd.DataFrame({
        'Date': ip_dates,
        'IP Patients': ip_counts,
        'New OP Patients': new_op_counts,
        'Total Unique Patients': total_unique_counts,
    })

st.title("Patient Data Analysis")

uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

if uploaded_file is not None:
    ip_df = pd.read_excel(uploaded_file, sheet_name='IP')
    new_op_df = pd.read_excel(uploaded_file, sheet_name='New OP')

    ip_df.columns = ip_df.columns.str.strip()
    new_op_df.columns = new_op_df.columns.str.strip()
    ip_df['APPT_DATE'] = pd.to_datetime(ip_df['APPT_DATE'])
    new_op_df['APPT_DATE'] = pd.to_datetime(new_op_df['APPT_DATE'])

    selected_date = st.date_input("Select Date", datetime.now().date())

    ip_processed = process_ip_data(ip_df, selected_date)
    new_op_processed = process_new_op_data(new_op_df, selected_date)
    combined_df = pd.concat([ip_processed, new_op_processed], ignore_index=True)

    st.subheader("Processed Data")
    st.dataframe(combined_df)

    csv = combined_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"patient_data_{selected_date}.csv",
        mime="text/csv"
    )

    st.subheader("Patient Trends (Last 30 Days)")
    historical_data = get_historical_data(ip_df, new_op_df)

    fig_bar = px.bar(
        historical_data,
        x='Date',
        y=['IP Patients', 'New OP Patients'],
        title="Daily Patient Counts",
        barmode='group'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_line = px.line(
        historical_data,
        x='Date',
        y=['IP Patients', 'New OP Patients'],
        title="Daily Patient Counts (Line Chart)",
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

