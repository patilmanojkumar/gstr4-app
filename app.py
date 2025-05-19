import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# Function to process the uploaded file
import pandas as pd

def process_file(uploaded_file):
    # Read the Excel file
    df = pd.read_excel(uploaded_file, sheet_name='B2B', skiprows=5)

    # Select and rename relevant columns
    df1 = df[['Unnamed: 1', 'Unnamed: 9', 'Unnamed: 10', 
              'Integrated tax  (₹)', 'Central tax (₹)', 
              'State/UT tax (₹)', 'Cess  (₹)']]
    df1.rename(columns={
        'Unnamed: 1': 'GSTIN of supplier',
        'Unnamed: 9': 'Rate (%)',
        'Unnamed: 10': 'Taxable value (₹)'
    }, inplace=True)

    # Clean numeric columns
    cols_to_clean = ['Taxable value (₹)', 'Integrated tax  (₹)', 
                     'Central tax (₹)', 'State/UT tax (₹)', 'Cess  (₹)']
    df1[cols_to_clean] = df1[cols_to_clean].replace('[^\d.]', '', regex=True)
    df1[cols_to_clean] = df1[cols_to_clean].apply(pd.to_numeric, errors='coerce')

    # Drop rows with missing group keys
    df1 = df1.dropna(subset=['GSTIN of supplier', 'Rate (%)'])

    # Group by 'GSTIN of supplier' and 'Rate (%)' and sum the other numeric columns
    grouped = df1.groupby(['GSTIN of supplier', 'Rate (%)'], as_index=False)[
        ['Taxable value (₹)', 'Integrated tax  (₹)', 'Central tax (₹)', 'State/UT tax (₹)', 'Cess  (₹)']
    ].sum()

    # Reorder columns explicitly
    ordered_columns = ['GSTIN of supplier', 'Taxable value (₹)', 'Rate (%)', 
                       'Integrated tax  (₹)', 'Central tax (₹)', 'State/UT tax (₹)', 'Cess  (₹)']
    grouped = grouped[ordered_columns]

    return grouped
import streamlit as st

def main():
    st.title("Upload the GSTR4A Excel file")
    
    # Upload file
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"], key='file_uploader')

    if uploaded_file is not None:
        st.success("File uploaded successfully!")  # Green success message

        # Process the uploaded file
        result = process_file(uploaded_file)

        # Download link for the processed file
        st.markdown(get_binary_file_downloader_html(result, file_label='<span style="color: green;"> the processed file</span>', file_name='processed-file.xlsx'), unsafe_allow_html=True)

# Function to create a download link for files
def get_binary_file_downloader_html(bin_file, file_label='File', file_name='file.xlsx'):
    with BytesIO() as f:
        bin_file.to_excel(f, index=False)
        data = f.getvalue()

    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Click here to download {file_label}</a>'
    return href

if __name__ == "__main__":
    main()
