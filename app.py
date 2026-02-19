import streamlit as st
import pandas as pd

st.set_page_config(page_title="Large Dataset Join App", layout="wide")

st.title("📊 Multi-Dataset Join Web Application")

dataset_type = st.selectbox(
    "Select Dataset Type",
    ["Education", "E-Commerce", "Healthcare", "Employee Management"]
)

join_type = st.selectbox(
    "Select Join Type",
    ["left", "inner", "right", "outer"]
)

st.sidebar.header("Upload CSV Files")

file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id"
}

if file1 and file2:

    with st.spinner("Processing large datasets... Please wait"):
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        join_column = join_keys[dataset_type]

        if join_column in df1.columns and join_column in df2.columns:

            final = pd.merge(df1, df2, on=join_column, how=join_type)

            st.success(f"Datasets Joined using '{join_type.upper()}' join on '{join_column}'")

            st.subheader("Preview (First 100 Rows)")
            st.dataframe(final.head(100))

            st.metric("Total Rows", len(final))

        csv = final.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Joined Dataset",
    data=csv,
    file_name="joined_dataset.csv",
    mime="text/csv",
)


        else:
            st.error(f"Selected dataset must contain column '{join_column}'")



