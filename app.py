import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Multi-Dataset Fusion Dashboard", layout="wide")

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
.stApp { background-color: #0f1c2e; }
section[data-testid="stSidebar"] { background-color: #0b1625; }
h1, h2, h3, h4, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "final_df" not in st.session_state:
    st.session_state.final_df = None

# =========================
# DOMAIN LIST
# =========================
domains = [
    "Education Analytics",
    "Healthcare Management",
    "E-Commerce & Retail",
    "Banking & Finance",
    "HR Management",
    "Supply Chain",
    "Telecommunications",
    "Real Estate",
    "Social Media Analytics",
    "Manufacturing"
]

st.title("📊 Multi-Dataset Fusion Dashboard")

domain = st.selectbox("📂 Select Business Domain", domains)

# =========================
# FILE UPLOAD
# =========================
uploaded_files = st.sidebar.file_uploader(
    "Upload at least 2 related datasets",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)

# =========================
# MERGE
# =========================
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols &= set(df.columns)

    if common_cols:
        join_column = st.selectbox("Select Join Column", list(common_cols))
        join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"])

        if st.button("Merge Datasets"):
            final = df_list[0]
            for df in df_list[1:]:
                final = final.merge(df, on=join_column, how=join_type)

            st.session_state.final_df = final
            st.success("Datasets merged successfully!")
    else:
        st.error("No common columns found.")

# =========================
# AFTER MERGE
# =========================
if st.session_state.final_df is not None:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()

    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=["number"]).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # =========================
    # KPI SECTION
    # =========================
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    # =========================
    # DATA SUMMARY (Instead of Visuals)
    # =========================
    st.subheader("📑 Dataset Summary")

    st.write("### Numerical Summary")
    st.dataframe(final.describe())

    st.write("### Preview of Data")
    st.dataframe(final.head())

    # =========================
    # EXPORT
    # =========================
    st.subheader("⬇ Export Data")

    st.download_button(
        "Download CSV",
        final.to_csv(index=False),
        "final_dataset.csv"
    )

    buffer = io.BytesIO()
    final.to_excel(buffer, index=False)

    st.download_button(
        "Download Excel",
        buffer.getvalue(),
        "final_dataset.xlsx"
    )

else:
    st.info("Upload at least 2 related datasets to begin.")
