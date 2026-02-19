import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Data Fusion Dashboard", layout="wide")

# ---------------- DARK NAVY THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0b1f3a;
}
section[data-testid="stSidebar"] {
    background-color: #071426;
}
h1, h2, h3, h4, label {
    color: #ffffff !important;
}
.stButton>button {
    background-color: #1f3c88;
    color: white;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}

# ==============================
# LOGIN PAGE
# ==============================
def login_page():
    st.title("🔐 Secure Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2, col3 = st.columns(3)

    if col1.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if col2.button("Create Account"):
        st.session_state.show_create = True

    if col3.button("Forgot Password"):
        if username in st.session_state.users:
            st.info(f"Password: {st.session_state.users[username]}")
        else:
            st.warning("Enter valid username to recover password")

def create_account():
    st.title("🆕 Create Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        st.session_state.users[new_user] = new_pass
        st.success("Account created! Please login.")
        st.session_state.show_create = False
        st.rerun()

# ---------------- AUTH ROUTING ----------------
if not st.session_state.logged_in:
    if "show_create" in st.session_state and st.session_state.show_create:
        create_account()
    else:
        login_page()
    st.stop()

# ==============================
# MAIN DASHBOARD
# ==============================

st.title("📊 Multi-Dataset Fusion Dashboard")

# -------- LOGOUT IN MAIN PAGE --------
main_logout_col = st.columns([8,1])
with main_logout_col[1]:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -------- SIDEBAR --------
st.sidebar.title("📁 Upload Datasets")

# -------- LOGOUT IN SIDEBAR --------
st.sidebar.markdown("## 🔐 Account")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# -------- DOMAINS --------
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

domain = st.selectbox("📂 Select Business Domain", domains)

# -------- FILE UPLOAD --------
uploaded_files = st.sidebar.file_uploader(
    "Upload Files (CSV, Excel, JSON)",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

# -------- FILE LOADER --------
@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)

# -------- PROCESS --------
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]

    # Clean column names
    df_list = [df.rename(columns=lambda x: x.strip()) for df in df_list]

    # -----------------------------
    # AUTO DETECT COMMON COLUMNS
    # -----------------------------
    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols = common_cols.intersection(set(df.columns))

    if not common_cols:
        st.error("❌ No common columns detected between datasets.")
        st.stop()

    # -----------------------------
    # DOMAIN INTELLIGENT SUGGESTION
    # -----------------------------
    domain_key_map = {
        "Education Analytics": ["student_id", "roll_no", "studentID"],
        "Healthcare Management": ["patient_id", "patientID", "medical_id"],
        "E-Commerce & Retail": ["order_id", "customer_id", "product_id"],
        "Banking & Finance": ["account_id", "customer_id"],
        "HR Management": ["employee_id", "emp_id"],
        "Supply Chain": ["shipment_id", "order_id"],
        "Telecommunications": ["customer_id", "phone_number"],
        "Real Estate": ["property_id", "agent_id"],
        "Social Media Analytics": ["user_id", "account_id"],
        "Manufacturing": ["product_id", "batch_id"]
    }

    suggested_keys = []
    for key in domain_key_map.get(domain, []):
        if key in common_cols:
            suggested_keys.append(key)

    st.subheader("🔍 Join Column Selection")

    if suggested_keys:
        st.success(f"Suggested join column(s) for {domain}: {suggested_keys}")
        join_column = st.selectbox(
            "Select Join Column",
            suggested_keys + list(common_cols)
        )
    else:
        st.warning("No domain-specific key found. Select manually.")
        join_column = st.selectbox("Select Join Column", list(common_cols))

    join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"])

    # -----------------------------
    # MERGE BUTTON (Controlled Execution)
    # -----------------------------
    if st.button("🚀 Merge Datasets"):

        final = df_list[0]
        for df in df_list[1:]:
            final = final.merge(df, on=join_column, how=join_type)

        st.success("Datasets merged successfully!")

        # -----------------------------
        # DATA CLEANING
        # -----------------------------
        st.subheader("🧹 Data Cleaning Options")

        if st.checkbox("Remove Duplicates"):
            final = final.drop_duplicates()

        if st.checkbox("Drop Null Rows"):
            final = final.dropna()

        if st.checkbox("Normalize Numeric Columns"):
            scaler = MinMaxScaler()
            num_cols = final.select_dtypes(include=np.number).columns
            final[num_cols] = scaler.fit_transform(final[num_cols])

        # -----------------------------
        # KPI SECTION
        # -----------------------------
        st.subheader("📊 KPI Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", final.shape[0])
        col2.metric("Columns", final.shape[1])
        col3.metric("Missing Values", final.isnull().sum().sum())

        # -----------------------------
        # AUTOMATIC INSIGHTS
        # -----------------------------
        st.subheader("🧠 Auto Insights")

        st.write("Missing Value %:")
        st.write((final.isnull().sum() / len(final) * 100).round(2))

        st.write("Duplicate Rows:", final.duplicated().sum())

        # -----------------------------
        # VISUAL ANALYTICS
        # -----------------------------
        st.subheader("📈 Visual Analytics")

        numeric_cols = final.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:

            selected_col = st.selectbox("Select Numeric Column", numeric_cols)

            colA, colB = st.columns(2)

            fig_bar = px.bar(final[selected_col].value_counts().head(10))
            colA.plotly_chart(fig_bar, use_container_width=True)

            fig_pie = px.pie(final, names=selected_col)
            colB.plotly_chart(fig_pie, use_container_width=True)

            fig_line = px.line(final[selected_col])
            st.plotly_chart(fig_line, use_container_width=True)

            corr = final[numeric_cols].corr()
            fig_heat = px.imshow(corr, text_auto=True)
            st.plotly_chart(fig_heat, use_container_width=True)

        # -----------------------------
        # ML OPTION
        # -----------------------------
        st.subheader("🤖 ML Option")

        if len(numeric_cols) >= 2:
            target = st.selectbox("Select Target Column", numeric_cols)
            features = final[numeric_cols].drop(columns=[target])

            if st.button("Run Regression"):
                model = LinearRegression()
                model.fit(features, final[target])
                st.success("Regression Model Trained Successfully")

            if st.button("Run Clustering"):
                kmeans = KMeans(n_clusters=3)
                final["Cluster"] = kmeans.fit_predict(features)
                st.success("Clustering Complete")
                st.dataframe(final.head())

        # -----------------------------
        # EXPORT
        # -----------------------------
        st.subheader("⬇ Export Data")

        csv = final.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "final_dataset.csv")

        buffer = io.BytesIO()
        final.to_excel(buffer, index=False)
        st.download_button("Download Excel", buffer, "final_dataset.xlsx")

        json_data = final.to_json().encode()
        st.download_button("Download JSON", json_data, "final_dataset.json")

else:
    st.info("Upload at least 2 files to begin.")
