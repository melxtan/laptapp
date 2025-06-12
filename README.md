# Patient Data Analysis Application

This Streamlit application processes and analyzes patient data from an Excel file containing IP (Inpatient) and New OP (New Outpatient) records.

## Features

- Upload and process Excel files with IP and New OP patient data
- Flexible column name handling (supports multiple possible column names)
- Filter and deduplicate patient records based on specific criteria
- Group New OP records within 20-day windows for the same MRN
- Generate downloadable CSV reports
- Visualize patient trends with interactive charts
- Track unique patient counts over time

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Upload your Excel file using the file uploader
3. Select a date using the date picker
4. View the processed data in the table
5. Download the results as a CSV file
6. Explore the patient trends using the interactive charts

## Data Requirements

The Excel file should contain two sheets:

### IP Sheet
Required columns:
- APPT_DATE (date of appointment/admission)
- PATIENT (patient name)
- MRN (Medical Record Number)
- MED_SERVICE (medical service)

### New OP Sheet
Required columns:
- APPT_DATE (date of appointment)
- NAME or PATIENT or PATIENT_NAME (patient name)
- MRN (Medical Record Number)
- MED_SERVICE or SERVICE (medical service)
- PATIENT_CLASS (to filter out Telemedicine)
- Optional: HOME_PHONE or PHONE
- Optional: EMAIL

## Data Processing

### IP Data Processing
- Filters records for the selected date
- Deduplicates based on MRN
- Adds empty HOME_PHONE and EMAIL columns
- Marks source as 'IP'

### New OP Data Processing
- Filters out Telemedicine records
- Groups records within 20 days for the same MRN
- Creates Group Admit Date and Group Discharge Date
- Deduplicates based on MRN and Group Admit Date
- Filters for records spanning the selected date
- Marks source as 'New OP'

## Output

The application generates:
- A combined dataset with patient information from both IP and New OP sources
- A downloadable CSV file with the following columns:
  - PATIENT
  - MRN
  - MED_SERVICE
  - HOME_PHONE
  - EMAIL
  - SOURCE (identifies if record is from IP or New OP)
- Interactive visualizations:
  - Bar chart showing daily patient counts
  - Line graph showing patient trends over the last 30 days 
