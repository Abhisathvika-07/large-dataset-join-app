import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Enterprise Data Fusion Dashboard", layout="wide")

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
.stApp { background-color: #0f1c2e; }
section[data-testid="stSidebar"] { background-color: #0b1625; }
h1, h2, h3, h4, label, p { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Enterprise Multi-Dataset Fusion Dashboard")

# =========================
# DOMAIN VALIDATION KEYWORDS
# =========================
domain_keywords = {
    "Education Analytics": ["student", "mark", "score", "grade", "gpa"],
    "Healthcare Management": ["patient", "hospital", "disease", "status"],
    "E-Commerce & Retail": ["product", "category", "sales", "price"],
    "Banking & Finance": ["account", "transaction", "amount", "balance"]
}

domain = st.selectbox("📂 Select Business Domain", list(domain_keywords.keys()))

# =========================
# FILE UPLOAD
# =========================
uploaded_files = st.sidebar.file_uploader(
    "Upload at least 2 related datasets",
    type=["csv"],
    accept_multiple_files=True
)

@st.cache_data
def load_file(file):
    return pd.read_csv(file)

# =========================
# MERGE + DOMAIN VALIDATION
# =========================
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    # ---- DOMAIN VALIDATION ----
    all_columns = []
    for df in df_list:
        all_columns.extend(df.columns.tolist())

    expected = domain_keywords[domain]
    match_count = sum(1 for k in expected for col in all_columns if k in col)

    if match_count < 2:
        st.error(f"❌ Uploaded dataset does NOT match selected domain: {domain}")
        st.stop()

    # ---- COMMON COLUMN ----
    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols &= set(df.columns)

    if not common_cols:
        st.error("❌ No common columns found to merge.")
        st.stop()

    join_column = st.selectbox("Select Join Column", list(common_cols))
    join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"])

    if st.button("Merge Datasets"):
        final = df_list[0]
        for df in df_list[1:]:
            final = final.merge(df, on=join_column, how=join_type)

        st.session_state.final_df = final
        st.success("Datasets merged successfully!")

# =========================
# AFTER MERGE
# =========================
if "final_df" in st.session_state:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()

    # ---------------- DATA CLEANING ----------------
    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=["number"]).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # ---------------- KPI ----------------
    st.subheader("📌 Key Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    # ---------------- DATA QUALITY SCORE ----------------
    st.subheader("📈 Data Quality Score")

    missing = final.isnull().sum().sum()
    total = final.size
    quality_score = round(((total - missing) / total) * 100, 2)
    st.metric("Data Quality (%)", quality_score)

    # ---------------- AUTOMATED INSIGHTS ----------------
    st.subheader("🧠 Automated Insights")

    numeric_cols = final.select_dtypes(include=["number"]).columns

    if len(numeric_cols) > 0:
        highest = final[numeric_cols].mean().idxmax()
        lowest = final[numeric_cols].mean().idxmin()

        st.success(f"Highest average metric: **{highest}** ({round(final[highest].mean(),2)})")
        st.warning(f"Lowest average metric: **{lowest}** ({round(final[lowest].mean(),2)})")

    # ---------------- FILTERING ----------------
    st.subheader("🔎 Advanced Filtering")

    filter_col = st.selectbox("Select Column to Filter", final.columns)

    if final[filter_col].dtype == "object":
        selected_val = st.selectbox("Select Value", final[filter_col].unique())
        filtered = final[final[filter_col] == selected_val]
    else:
        min_val = float(final[filter_col].min())
        max_val = float(final[filter_col].max())
        selected_range = st.slider("Select Range", min_val, max_val, (min_val, max_val))
        filtered = final[
            (final[filter_col] >= selected_range[0]) &
            (final[filter_col] <= selected_range[1])
        ]

    st.write("Filtered Preview")
    st.dataframe(filtered.head())

    # ---------------- CORRELATION ----------------
    st.subheader("📊 Correlation Heatmap")

    if len(numeric_cols) > 1:
        corr = final[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, title="Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- TOP / BOTTOM ANALYSIS ----------------
    st.subheader("🏆 Top / Bottom Analysis")

    if len(numeric_cols) > 0:
        metric_col = st.selectbox("Select Metric", numeric_cols)

        st.write("Top 5 Records")
        st.dataframe(final.sort_values(metric_col, ascending=False).head())

        st.write("Bottom 5 Records")
        st.dataframe(final.sort_values(metric_col).head())

   
   # ---------------- COLUMN SEARCH (Improved) ----------------
st.subheader("🔍 Column Search")

search_term = st.text_input("Search Column Name")

if search_term:
    matching = [col for col in final.columns 
                if search_term.lower() in col.lower()]

    if matching:
        st.success(f"Found {len(matching)} matching column(s):")

        for col in matching:
            st.write(f"✔ {col}")

            # Show preview of that column
            st.write(final[[col]].head())

    else:
        st.error("❌ No matching columns found.")

    # ---------------- DATA PREVIEW ----------------
    st.subheader("📑 Full Data Preview")
    st.dataframe(final.head())

    # ---------------- EXPORT ----------------
    st.subheader("⬇ Export Options")

    csv_full = final.to_csv(index=False)
    st.download_button("Download Full Dataset", csv_full, "full_dataset.csv")

    csv_filtered = filtered.to_csv(index=False)
    st.download_button("Download Filtered Dataset", csv_filtered, "filtered_dataset.csv")

else:
    st.info("Upload at least 2 related datasets to begin.")

