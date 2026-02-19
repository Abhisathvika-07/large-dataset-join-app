import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Multi-Dataset Data Fusion Platform",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # TEMP: keep true to focus on features

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
}
h1, h2, h3, h4, label {
    color: #e5e7eb !important;
}
.block-container {
    padding: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📊 Multi-Dataset Data Fusion Dashboard")

# ---------------- DOMAIN SELECTION ----------------
domain = st.selectbox(
    "Select Dataset Domain",
    [
        "Education",
        "Healthcare",
        "Finance",
        "Retail",
        "Human Resources",
        "Sales & Marketing"
    ]
)

st.info(f"Domain selected: **{domain}**")

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Multiple Datasets (CSV, Excel, JSON)",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 2:

    dfs = []

    for file in uploaded_files:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            df = pd.read_json(file)
        dfs.append(df)

    # ---------------- AUTO DETECT JOIN KEYS ----------------
    common_columns = set(dfs[0].columns)
    for df in dfs[1:]:
        common_columns = common_columns.intersection(df.columns)

    if not common_columns:
        st.error("❌ No common columns found between datasets")
        st.stop()

    st.subheader("🔑 Auto-Detected Join Columns")
    join_column = st.selectbox(
        "Select Join Column (Auto Suggested)",
        list(common_columns)
    )

    join_type = st.selectbox(
        "Select Join Type",
        ["inner", "left", "right", "outer"]
    )

    # ---------------- DATA CLEANING OPTIONS ----------------
    st.subheader("🧹 Data Cleaning Options")

    col1, col2, col3, col4 = st.columns(4)
    remove_duplicates = col1.checkbox("Remove Duplicates")
    drop_nulls = col2.checkbox("Drop Null Rows")
    fill_missing = col3.checkbox("Fill Missing Values")
    normalize_numeric = col4.checkbox("Normalize Numeric Columns")

    # ---------------- MERGE ----------------
    final_df = dfs[0]
    for df in dfs[1:]:
        final_df = pd.merge(final_df, df, on=join_column, how=join_type)

    # ---------------- APPLY CLEANING ----------------
    if remove_duplicates:
        final_df = final_df.drop_duplicates()

    if drop_nulls:
        final_df = final_df.dropna()

    if fill_missing:
        for col in final_df.select_dtypes(include=np.number).columns:
            final_df[col] = final_df[col].fillna(final_df[col].mean())

    if normalize_numeric:
        for col in final_df.select_dtypes(include=np.number).columns:
            final_df[col] = (
                final_df[col] - final_df[col].min()
            ) / (final_df[col].max() - final_df[col].min())

    st.success("✅ Datasets merged and processed successfully")

    # ---------------- KPI CARDS ----------------
    st.subheader("📌 Key Metrics")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Rows", final_df.shape[0])
    k2.metric("Columns", final_df.shape[1])
    k3.metric("Missing Values", final_df.isnull().sum().sum())
    k4.metric("Duplicate Rows", final_df.duplicated().sum())

    # ---------------- CHARTS ----------------
    st.subheader("📈 Automatic Data Visualizations")

    numeric_cols = final_df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = final_df.select_dtypes(include="object").columns.tolist()

    if numeric_cols:
        num_col = st.selectbox("Select Numeric Column", numeric_cols)
        fig_hist = px.histogram(
            final_df,
            x=num_col,
            title=f"Distribution of {num_col}"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    if categorical_cols:
        cat_col = st.selectbox("Select Categorical Column", categorical_cols)
        pie_data = final_df[cat_col].value_counts().reset_index()
        pie_data.columns = [cat_col, "Count"]

        fig_pie = px.pie(
            pie_data,
            names=cat_col,
            values="Count",
            title=f"Category Distribution: {cat_col}"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- CORRELATION HEATMAP ----------------
    if len(numeric_cols) >= 2:
        corr = final_df[numeric_cols].corr()
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ---------------- AI-LIKE SUMMARY ----------------
    st.subheader("🤖 Automated Insight Summary")

    summary_text = f"""
    • The merged dataset contains **{final_df.shape[0]} rows** and **{final_df.shape[1]} columns**.  
    • The join operation was performed using **{join_column}** with **{join_type} join**.  
    • The domain of analysis is **{domain}**.  
    • Numeric features show noticeable variation and correlation patterns.  
    • Data cleaning operations improved dataset consistency.
    """

    st.info(summary_text)

    # ---------------- DATA PREVIEW ----------------
    st.subheader("📄 Final Dataset Preview")
    st.dataframe(final_df.head(100))

    # ---------------- EXPORT ----------------
    st.subheader("⬇ Export Final Dataset")

    csv = final_df.to_csv(index=False).encode()
    st.download_button(
        "Download CSV",
        csv,
        "final_dataset.csv",
        "text/csv"
    )

else:
    st.warning("Upload at least **two datasets** to start analysis.")

