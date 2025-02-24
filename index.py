# Imports
import streamlit as st
import numpy as np
import pandas as pd
import os
import time  # For progress bar
from io import BytesIO

# Ensure Streamlit page config is set FIRST
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Title & Intro
st.title("🧹 Data Sweeper")
st.write("Upload your data, clean it, and download it in a structured format.")

# Ensure xlsxwriter is installed
try:
    import xlsxwriter
except ImportError:
    st.warning("⚠️ `xlsxwriter` is missing! Run: `pip install xlsxwriter`")

# File uploader
uploaded_files = st.file_uploader("📤 Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Validate file format
        if file_ext not in [".csv", ".xlsx"]:
            st.error(f"❌ Invalid file: {file.name}. Only CSV or Excel files are allowed.")
            continue  # Skip processing this file

        # Try reading file
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            else:  # ".xlsx"
                df = pd.read_excel(file)
        except Exception as e:
            st.error(f"⚠️ Error reading {file.name}: {e}")
            continue  # Skip processing

        # File info
        st.write(f"**📁 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.getbuffer().nbytes / 1024:.2f} KB")

        # Data preview
        st.write("🔍 **Data Preview:**")
        st.dataframe(df.head())

        # Expander for data cleaning options
        with st.expander(f"🛠️ Cleaning Options for {file.name}"):
            st.subheader("🧹 Data Cleaning")

            # Remove Duplicates
            if st.button(f"Remove Duplicates from {file.name}", key=f"dup_{file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("✅ Duplicates removed.")

            # Fill Missing Values
            if st.button(f"Fill Missing Values for {file.name}", key=f"fill_{file.name}"):
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✅ Missing values filled with column means.")

            # Column Selection
            st.subheader("📌 Select Columns to Keep")
            selected_columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]  # Keep only selected columns

            # Data Visualization
            st.subheader("📊 Data Visualization")
            if st.checkbox(f"Show Bar Chart for {file.name}"):
                numeric_data = df.select_dtypes(include=['number']).dropna()
                if not numeric_data.empty:
                    st.bar_chart(numeric_data)
                else:
                    st.warning("⚠️ No numeric data available for visualization.")

            # Conversion Options
            st.subheader("🔄 Convert & Download")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"Convert & Download {file.name}", key=f"convert_{file.name}"):
                buffer = BytesIO()

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                else:  # "Excel"
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    buffer.seek(0)  # Reset buffer before download
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                # Show progress bar while processing
                with st.spinner("🔄 Processing..."):
                    time.sleep(1.5)  # Simulating work

                # Download button
                st.download_button(
                    label=f"📥 Download {file_name}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

# Thank you message
st.success("🎉 Thanks for using Data Sweeper! Give us a ⭐ on [GitHub](https://github.com/Palwasha-48).")
