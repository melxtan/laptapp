# Patient Data Analysis Application

This Streamlit application processes patient data from an Excel file and provides analysis and visualization tools.

## Features

- Upload and process Excel files with IP and New OP patient data
- Filter and deduplicate patient records based on specific criteria
- Group New OP records within 20-day windows
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
- "IP" sheet with columns: Date, NAME, MRN, MED_SERVICE
- "New OP" sheet with columns: NAME, MRN, MED_SERVICE, HOME_PHONE, EMAIL, PATIENT_CLASS, APPT_DATE

## Output

The application generates:
- A combined dataset with patient information from both IP and New OP sources
- A downloadable CSV file
- Interactive visualizations showing patient trends over the last 30 days 
