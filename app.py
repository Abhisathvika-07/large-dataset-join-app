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

# ---------------- DOMAIN LIST ----------------
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

# ---------------- FILE UPLOAD ----------------
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

# ---------------- MERGE ----------------
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

# ---------------- AFTER MERGE ----------------
if st.session_state.final_df is not None:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()

    # Remove obvious ID columns
    final = final[[col for col in final.columns if "id" not in col]]

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

    numeric_cols = final.select_dtypes(include=["number"]).columns
    categorical_cols = final.select_dtypes(include=["object"]).columns

    if len(numeric_cols) > 0 and len(categorical_cols) > 0:

        value_col = numeric_cols[0]
        category_col = categorical_cols[0]

        # ---------------- BAR CHART ----------------
        fig_bar = px.bar(
            final,
            x=category_col,
            y=value_col,
            labels={
                category_col: category_col.replace("_", " ").title(),
                value_col: value_col.replace("_", " ").title()
            },
            title=f"{value_col.replace('_',' ').title()} by {category_col.replace('_',' ').title()}"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.write(
            f"This bar chart compares {value_col.replace('_',' ')} across different {category_col.replace('_',' ')} categories, helping identify highest and lowest values."
        )

        # ---------------- LINE CHART ----------------
        fig_line = px.line(
            final,
            x=category_col,
            y=value_col,
            markers=True,
            labels={
                category_col: category_col.replace("_", " ").title(),
                value_col: value_col.replace("_", " ").title()
            },
            title=f"Trend of {value_col.replace('_',' ').title()}"
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.write(
            f"This line chart shows how {value_col.replace('_',' ')} changes across {category_col.replace('_',' ')}, revealing patterns or trends."
        )

        # ---------------- PIE CHART ----------------
        pie_counts = final[category_col].value_counts().reset_index()
        pie_counts.columns = ["Category", "Count"]

        fig_pie = px.pie(
            pie_counts,
            values="Count",
            names="Category",
            title=f"Distribution of {category_col.replace('_',' ').title()}"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.write(
            f"This pie chart illustrates the percentage distribution of different {category_col.replace('_',' ')} categories."
        )

    else:
        st.warning("Dataset needs at least one numeric and one categorical column for visualization.")

else:
    st.info("Upload at least 2 related datasets to begin analysis.")
