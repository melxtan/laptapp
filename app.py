import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Set page config
st.set_page_config(page_title="Patient Data Analysis", layout="wide")

def safe_get_col(df, keys, fill=''):
    for key in keys:
        if key in df.columns:
            return df[key]
    return fill

# Function to process IP data
def process_ip_data(df, selected_date):
    # Convert selected_date to datetime
    selected_date = pd.to_datetime(selected_date)
    # Filter for selected date
    df = df[df['APPT_DATE'] == selected_date]
    # Deduplicate based on MRN
    df = df.drop_duplicates(subset=['MRN'])
    # Select and rename columns
    df = df[['PATIENT', 'MRN', 'MED_SERVICE']]
    # Add source column
    df['SOURCE'] = 'IP'
    # Add empty columns for HOME_PHONE and EMAIL
    df['HOME_PHONE'] = ''
    df['EMAIL'] = ''
    return df

# Function to process New OP data
def process_new_op_data(df, selected_date):
    # Convert selected_date to datetime
    selected_date = pd.to_datetime(selected_date)
    
    # Filter out Telemedicine
    df = df[df['PATIENT_CLASS'] != 'Telemedicine']
    
    # Convert APPT_DATE to datetime if it's not already
    df['APPT_DATE'] = pd.to_datetime(df['APPT_DATE'])
    
    # Sort by MRN and APPT_DATE
    df = df.sort_values(['MRN', 'APPT_DATE'])
    
    # Initialize group columns
    df['Group Admit Date'] = df['APPT_DATE']
    df['Group Discharge Date'] = df['APPT_DATE']
    
    # Group records within 20 days for same MRN
    current_group = 0
    current_mrn = None
    current_start = None
    
    for idx, row in df.iterrows():
        if current_mrn != row['MRN'] or (current_start and (row['APPT_DATE'] - current_start).days > 20):
            current_group += 1
            current_mrn = row['MRN']
            current_start = row['APPT_DATE']
        
        df.at[idx, 'Group Admit Date'] = current_start
        df.at[idx, 'Group Discharge Date'] = row['APPT_DATE']
    
    # Filter for selected date
    df = df[(df['Group Admit Date'] <= selected_date) & (df['Group Discharge Date'] >= selected_date)]
    
    # Deduplicate based on MRN and Group Admit Date
    df = df.drop_duplicates(subset=['MRN', 'Group Admit Date'])
    
    # Create a new dataframe with required columns
    result_df = pd.DataFrame()
    result_df['PATIENT'] = safe_get_col(df, ['NAME', 'PATIENT', 'PATIENT_NAME'])
    result_df['MRN'] = safe_get_col(df, ['MRN'])
    result_df['MED_SERVICE'] = safe_get_col(df, ['MED_SERVICE', 'SERVICE'])
    result_df['HOME_PHONE'] = safe_get_col(df, ['HOME_PHONE', 'PHONE'])
    result_df['EMAIL'] = safe_get_col(df, ['EMAIL'])
    result_df['SOURCE'] = 'New OP'

    
    # Add HOME_PHONE and EMAIL if they exist, otherwise add empty columns
    if 'HOME_PHONE' in df.columns:
        result_df['HOME_PHONE'] = df['HOME_PHONE']
    else:
        result_df['HOME_PHONE'] = ''
        
    if 'EMAIL' in df.columns:
        result_df['EMAIL'] = df['EMAIL']
    else:
        result_df['EMAIL'] = ''
    
    # Add source column
    result_df['SOURCE'] = 'New OP'
    return result_df

# Function to get historical data for visualization
def get_historical_data(ip_df, new_op_df, days=30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    ip_dates = pd.date_range(start=start_date, end=end_date)
    ip_counts = []
    for date in ip_dates:
        count = len(ip_df[ip_df['APPT_DATE'].dt.date == date.date()]['MRN'].unique())
        ip_counts.append(count)
    
    # Make sure new_op_df['APPT_DATE'] is datetime outside this function!
    new_op_counts = []
    for date in ip_dates:
        count = len(new_op_df[
            (new_op_df['APPT_DATE'].dt.date == date.date()) & 
            (new_op_df['PATIENT_CLASS'] != 'Telemedicine')
        ]['MRN'].unique())
        new_op_counts.append(count)
    
    return pd.DataFrame({
        'Date': ip_dates,
        'IP Patients': ip_counts,
        'New OP Patients': new_op_counts
    })

# Main app
st.title("Patient Data Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

if uploaded_file is not None:
    # Read Excel file
    ip_df = pd.read_excel(uploaded_file, sheet_name='IP')
    new_op_df = pd.read_excel(uploaded_file, sheet_name='New OP')

    # Clean column names (good practice)
    ip_df.columns = ip_df.columns.str.strip()
    new_op_df.columns = new_op_df.columns.str.strip()

    # Convert APPT_DATE columns to datetime
    ip_df['APPT_DATE'] = pd.to_datetime(ip_df['APPT_DATE'])
    new_op_df['APPT_DATE'] = pd.to_datetime(new_op_df['APPT_DATE'])

    # Date selector
    selected_date = st.date_input("Select Date", datetime.now().date())

    # Process data for the selected date
    ip_processed = process_ip_data(ip_df, selected_date)
    new_op_processed = process_new_op_data(new_op_df, selected_date)

    # Combine results
    combined_df = pd.concat([ip_processed, new_op_processed], ignore_index=True)

    # Display processed data
    st.subheader("Processed Data")
    st.dataframe(combined_df)

    # Download button
    csv = combined_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"patient_data_{selected_date}.csv",
        mime="text/csv"
    )

    # Visualization for trends (last 30 days)
    st.subheader("Patient Trends (Last 30 Days)")
    historical_data = get_historical_data(ip_df, new_op_df)  # This function does the counting

    # Bar chart
    fig_bar = px.bar(
        historical_data,
        x='Date',
        y=['IP Patients', 'New OP Patients'],
        title="Daily Patient Counts",
        barmode='group'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Line graph
    fig_line = px.line(
        historical_data,
        x='Date',
        y=['IP Patients', 'New OP Patients'],
        title="Patient Trends Over Time"
    )
    st.plotly_chart(fig_line, use_container_width=True)
