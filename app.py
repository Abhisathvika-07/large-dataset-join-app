import streamlit as st
import pandas as pd

st.set_page_config(page_title="Large Dataset Join App", layout="wide")

st.title("📊 Multi-Dataset Join Web Application")

# -------------------------
# Dataset Type Selection
# -------------------------
dataset_type = st.selectbox(
    "Select Dataset Type",
    ["Education", "E-Commerce", "Healthcare", "Employee Management"]
)

st.sidebar.header("Upload CSV Files")

file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

# -------------------------
# Join Key Logic
# -------------------------
join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id"
}

if file1 and file2:

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    join_column = join_keys[dataset_type]

    if join_column in df1.columns and join_column in df2.columns:

        final = pd.merge(df1, df2, on=join_column, how="left")

        st.success(f"Datasets Joined on '{join_column}' Successfully!")

        st.subheader("Preview (First 100 Rows)")
        st.dataframe(final.head(100))

        st.metric("Total Rows", len(final))

    else:
        st.error(f"Selected dataset must contain column '{join_column}'")
