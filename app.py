import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Enterprise Analytics Platform",
    layout="wide",
    page_icon="📊"
)

# -----------------------------
# LOGIN AUTH (Simple Demo)
# -----------------------------
def login():
    st.markdown("## 🔐 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid Credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# -----------------------------
# POWER BI STYLE BACKGROUND
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
    color: white;
}

h1, h2, h3 {
    color: #f8fafc;
}

.metric-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: 0.3s;
}

.metric-card:hover {
    transform: scale(1.05);
    background-color: #334155;
}

.fade-in {
    animation: fadeIn 1.5s ease-in;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER WITH LOGO
# -----------------------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968350.png", width=80)

with col_title:
    st.markdown("<h1 class='fade-in'>Enterprise Data Intelligence Dashboard</h1>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# DATASET CATEGORY
# -----------------------------
dataset_type = st.selectbox(
    "Select Business Domain",
    [
        "Education",
        "Healthcare",
        "Employee Management",
        "E-Commerce",
        "Banking & Finance",
        "Retail Sales",
        "Supply Chain",
        "Telecommunications",
        "Insurance",
        "Logistics",
        "Marketing Analytics",
        "Government Data"
    ]
)

join_type = st.selectbox(
    "Select Join Strategy",
    ["inner", "left", "right", "outer"]
)

st.markdown("---")

# -----------------------------
# FILE UPLOAD
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload Primary Dataset", type=["csv"])

with col2:
    file2 = st.file_uploader("Upload Secondary Dataset", type=["csv"])

# -----------------------------
# JOIN KEY MAP
# -----------------------------
join_keys = {
    "Education": "student_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id",
    "E-Commerce": "customer_id",
    "Banking & Finance": "account_id",
    "Retail Sales": "order_id",
    "Supply Chain": "product_id",
    "Telecommunications": "subscriber_id",
    "Insurance": "policy_id",
    "Logistics": "shipment_id",
    "Marketing Analytics": "campaign_id",
    "Government Data": "citizen_id"
}

# -----------------------------
# PROCESSING
# -----------------------------
if file1 and file2:

    with st.spinner("Performing Enterprise Data Merge..."):

        df1 = pd.read_csv(file1, low_memory=False)
        df2 = pd.read_csv(file2, low_memory=False)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        join_column = join_keys[dataset_type]

        if join_column in df1.columns and join_column in df2.columns:

            final = pd.merge(df1, df2, on=join_column, how=join_type)

            st.success(f"Data Integrated Successfully using {join_type.upper()} join")

            # -----------------------------
            # KPI CARDS
            # -----------------------------
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"<div class='metric-card'><h3>Total Records</h3><h2>{len(final)}</h2></div>", unsafe_allow_html=True)

            with c2:
                st.markdown(f"<div class='metric-card'><h3>Total Columns</h3><h2>{len(final.columns)}</h2></div>", unsafe_allow_html=True)

            with c3:
                st.markdown(f"<div class='metric-card'><h3>Join Type</h3><h2>{join_type.upper()}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")

            # -----------------------------
            # DATA PREVIEW
            # -----------------------------
            st.subheader("Dataset Preview")
            st.dataframe(final.head(100), use_container_width=True)

            st.markdown("---")

            # -----------------------------
            # DOWNLOAD
            # -----------------------------
            csv = final.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Merged Dataset",
                csv,
                "enterprise_merged.csv",
                "text/csv"
            )

            st.markdown("---")

            # -----------------------------
            # VISUALIZATION
            # -----------------------------
            st.subheader("Business Intelligence Visualizations")

            numeric_cols = final.select_dtypes(include=["int64", "float64"]).columns

            if len(numeric_cols) > 0:

                selected_col = st.selectbox("Select Numeric KPI", numeric_cols)

                colA, colB = st.columns(2)

                with colA:
                    fig_bar = px.bar(final[selected_col].value_counts().head(10),
                                     title="Top 10 Distribution")
                    st.plotly_chart(fig_bar, use_container_width=True)

                with colB:
                    fig_pie = px.pie(final, names=selected_col,
                                     title="Pie Chart View")
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("---")

                fig_line = px.line(final[selected_col],
                                   title="Trend Analysis")
                st.plotly_chart(fig_line, use_container_width=True)

            else:
                st.info("No numeric KPI columns detected.")

        else:
            st.error(f"Join column '{join_column}' not found in both datasets.")

else:
    st.info("Upload both datasets to start enterprise processing.")

