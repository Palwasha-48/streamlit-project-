# Ensure xlsxwriter is installed
try:
    import xlsxwriter
except ImportError:
    import sys
    sys.exit("❌ Missing dependency: xlsxwriter. Install it using 'pip install xlsxwriter'.")

# Imports
import streamlit as st
import numpy as np
import pandas as pd
import os
from io import BytesIO

# ✅ Set page config at the very top
st.set_page_config(page_title="Data Sweeper", layout="wide")

# App title and description
st.title("Data Sweeper")
st.write("This is a simple tool to help you clean your data. Upload your data and start cleaning it.")

# File uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # File reading with error handling
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"❌ Please upload a valid CSV or Excel file.")
                continue
        except Exception as e:
            st.error(f"⚠️ Error reading {file.name}: {e}")
            continue

        # File info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.getbuffer().nbytes / 1024:.2f} KB")

        # Show data preview
        st.write("Preview of the data:")
        st.dataframe(df.head())

        # Expander for Data Cleaning & Processing Options
        with st.expander(f"Options for {file.name}"):
            st.subheader("🛠️ Data Cleaning Options")

            # Remove Duplicates
            if st.button(f"Remove Duplicates from {file.name}"):
                df.drop_duplicates(inplace=True)
                st.write("✅ Duplicates removed successfully.")

            # Fill Missing Values
            if st.button(f"Fill Missing Values for {file.name}"):
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.write("✅ Missing values filled successfully.")

            # Column Selection
            st.subheader("📌 Select Columns to Keep")
            columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Data Visualization
            st.subheader("📊 Data Visualization")
            if st.checkbox(f"Show Data Visualization for {file.name}"):
                numeric_data = df.select_dtypes(include=['number']).dropna()
                if numeric_data.shape[1] >= 1:
                    st.bar_chart(numeric_data)
                else:
                    st.write("⚠️ No valid numeric data available for visualization.")

            # Conversion Options
            st.subheader("🔄 Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)

                # Download button
                st.download_button(
                    label=f"📥 Download {file_name}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

# Thank you message with GitHub link
st.success("🎉 Thank you for using Data Sweeper. Please give us a ⭐ on [GitHub](https://github.com/Palwasha-48) if you liked it.")
