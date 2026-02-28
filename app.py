import streamlit as st
import pandas as pd
import plotly.express as px
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
    columns = final.columns

    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=["number"]).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    st.subheader("📊 Domain Based Visual Analytics")

    # -------- SMART COLUMN FINDER --------
    def find_column(keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    # =========================
    # EDUCATION
    # =========================
    if domain == "Education Analytics":
        value_col = find_column(["mark", "score"])
        category_col = find_column(["student", "name"])
        pie_col = find_column(["grade"])

    # =========================
    # HEALTHCARE
    # =========================
    elif domain == "Healthcare Management":
        value_col = find_column(["cost", "bill", "charge"])
        category_col = find_column(["hospital", "patient"])
        pie_col = find_column(["disease"])

    # =========================
    # E-COMMERCE
    # =========================
    elif domain == "E-Commerce & Retail":
        value_col = find_column(["price", "amount", "sales"])
        category_col = find_column(["product"])
        pie_col = find_column(["category"])

    # =========================
    # BANKING
    # =========================
    elif domain == "Banking & Finance":
        value_col = find_column(["amount", "transaction"])
        category_col = find_column(["account"])
        pie_col = find_column(["type"])

    # =========================
    # HR
    # =========================
    elif domain == "HR Management":
        value_col = find_column(["salary"])
        category_col = find_column(["department"])
        pie_col = find_column(["role"])

    # =========================
    # SUPPLY CHAIN
    # =========================
    elif domain == "Supply Chain":
        value_col = find_column(["shipment", "quantity"])
        category_col = find_column(["supplier"])
        pie_col = find_column(["status"])

    # =========================
    # TELECOM
    # =========================
    elif domain == "Telecommunications":
        value_col = find_column(["call", "usage"])
        category_col = find_column(["subscriber"])
        pie_col = find_column(["plan"])

    # =========================
    # REAL ESTATE
    # =========================
    elif domain == "Real Estate":
        value_col = find_column(["price", "rent"])
        category_col = find_column(["property"])
        pie_col = find_column(["type"])

    # =========================
    # SOCIAL MEDIA
    # =========================
    elif domain == "Social Media Analytics":
        value_col = find_column(["engagement", "likes"])
        category_col = find_column(["user"])
        pie_col = find_column(["post"])

    # =========================
    # MANUFACTURING
    # =========================
    elif domain == "Manufacturing":
        value_col = find_column(["production", "output"])
        category_col = find_column(["machine"])
        pie_col = find_column(["shift"])

    # =========================
    # GENERATE VISUALS
    # =========================
    if value_col:

        st.metric("Average Value", round(final[value_col].mean(), 2))

        # BAR
        fig_bar = px.bar(final,
                         x=category_col if category_col else final.index,
                         y=value_col,
                         title=f"{value_col} by {category_col if category_col else 'Index'}")
        st.plotly_chart(fig_bar, use_container_width=True)

        # LINE
        fig_line = px.line(final,
                           y=value_col,
                           markers=True,
                           title=f"{value_col} Trend")
        st.plotly_chart(fig_line, use_container_width=True)

        # PIE
        if pie_col:
            pie_counts = final[pie_col].value_counts().reset_index()
            pie_counts.columns = ["Category", "Count"]

            fig_pie = px.pie(pie_counts,
                             values="Count",
                             names="Category",
                             title=f"{pie_col} Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.warning("No domain-relevant numeric column found. Showing fallback charts.")

        numeric_cols = final.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            fallback = numeric_cols[0]

            fig_bar = px.bar(final, y=fallback)
            st.plotly_chart(fig_bar, use_container_width=True)

            fig_line = px.line(final, y=fallback)
            st.plotly_chart(fig_line, use_container_width=True)

else:
    st.info("Upload at least 2 related datasets to begin.")
