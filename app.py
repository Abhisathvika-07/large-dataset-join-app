import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Large Dataset Join App",
    layout="wide",
    page_icon="📊"
)

# -----------------------------
# CUSTOM CSS STYLING
# -----------------------------
st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}

h1, h2, h3 {
    color: #ffffff;
    text-align: center;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.css-1d391kg {
    background-color: #111;
}

.stSelectbox, .stFileUploader {
    background-color: #1e293b;
    padding: 10px;
    border-radius: 10px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
}

.stDownloadButton>button {
    background-color: #16a34a;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<h1>📊 Multi-Dataset Join Web Application</h1>
<p style='text-align:center; font-size:18px; color:#cbd5e1;'>
Professional Data Engineering Tool for Large Dataset Processing
</p>
""", unsafe_allow_html=True)

st.divider()

# -----------------------------
# DATASET TYPE
# -----------------------------
dataset_type = st.selectbox(
    "📂 Select Dataset Type",
    ["Education", "E-Commerce", "Healthcare", "Employee Management"]
)

# -----------------------------
# JOIN TYPE
# -----------------------------
join_type = st.selectbox(
    "🔗 Select Join Type",
    ["inner", "left", "right", "outer"]
)

# -----------------------------
# SIDEBAR UPLOAD
# -----------------------------
st.sidebar.markdown("## 📁 Upload CSV Files")

file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

# -----------------------------
# AUTO JOIN KEY
# -----------------------------
join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id"
}

if file1 and file2:

    with st.spinner("Processing large datasets... Please wait ⏳"):

        df1 = pd.read_csv(file1, low_memory=False)
        df2 = pd.read_csv(file2, low_memory=False)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        join_column = join_keys[dataset_type]

        if join_column in df1.columns and join_column in df2.columns:

            final = pd.merge(
                df1,
                df2,
                on=join_column,
                how=join_type
            )

            st.success(
                f"✅ Joined using '{join_type.upper()}' join on '{join_column}'"
            )

            st.divider()

            # -----------------------------
            # METRICS SECTION
            # -----------------------------
            col1, col2 = st.columns(2)
            col1.metric("📄 Total Rows", len(final))
            col2.metric("📊 Total Columns", len(final.columns))

            st.divider()

            # -----------------------------
            # PREVIEW
            # -----------------------------
            st.subheader("🔎 Preview (First 100 Rows)")
            st.dataframe(final.head(100), use_container_width=True)

            st.divider()

            # -----------------------------
            # DOWNLOAD BUTTON
            # -----------------------------
            csv = final.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇ Download Merged Dataset",
                data=csv,
                file_name="merged_dataset.csv",
                mime="text/csv"
            )

            st.divider()

            # -----------------------------
            # VISUALIZATION
            # -----------------------------
            st.subheader("📈 Data Visualization")

            numeric_cols = final.select_dtypes(
                include=["int64", "float64"]
            ).columns

            if len(numeric_cols) > 0:
                selected_col = st.selectbox(
                    "Select Numeric Column for Chart",
                    numeric_cols
                )
                st.bar_chart(
                    final[selected_col].value_counts().head(10)
                )
            else:
                st.info("No numeric columns available for visualization.")

        else:
            st.error(
                f"Selected dataset must contain column '{join_column}'"
            )

else:
    st.info("Please upload both CSV files to begin.")
