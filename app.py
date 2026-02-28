import streamlit as st
import pandas as pd
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
# DOMAIN DEFINITIONS (STRICT VALIDATION)
# =========================
domain_keywords = {
    "Education Analytics": ["student", "mark", "score", "grade"],
    "Healthcare Management": ["patient", "hospital", "disease", "status"],
    "E-Commerce & Retail": ["product", "category", "price", "sales"],
    "Banking & Finance": ["account", "transaction", "amount", "balance"],
    "HR Management": ["employee", "salary", "department", "role"],
    "Supply Chain": ["shipment", "supplier", "inventory", "status"],
    "Telecommunications": ["subscriber", "call", "plan", "usage"],
    "Real Estate": ["property", "rent", "buyer", "price"],
    "Social Media Analytics": ["user", "post", "engagement", "likes"],
    "Manufacturing": ["machine", "production", "factory", "output"]
}

st.title("📊 Multi-Dataset Fusion Dashboard")

domain = st.selectbox("📂 Select Business Domain", list(domain_keywords.keys()))

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
# MERGE + DOMAIN VALIDATION
# =========================
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    # ---- STRICT DOMAIN VALIDATION ----
    all_columns = []
    for df in df_list:
        all_columns.extend(df.columns.tolist())

    expected_keywords = domain_keywords[domain]

    match_count = 0
    for keyword in expected_keywords:
        for col in all_columns:
            if keyword in col:
                match_count += 1

    if match_count < 2:
        st.error(f"❌ Uploaded dataset does NOT match the selected domain: {domain}")
        st.stop()

    # ---- FIND COMMON COLUMNS ----
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
if st.session_state.final_df is not None:

    final = st.session_state.final_df

    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=["number"]).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # KPI SECTION
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    st.subheader("📑 Data Preview")
    st.dataframe(final.head())

    # EXPORT
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
