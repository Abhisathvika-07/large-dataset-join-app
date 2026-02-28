import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Multi-Dataset Fusion Dashboard", layout="wide")

# ---------------- THEME ----------------
st.markdown("""
<style>
.stApp { background-color: #0f1c2e; }
section[data-testid="stSidebar"] { background-color: #0b1625; }
h1, h2, h3, h4, label { color: white !important; }
.stButton>button {
    background-color: #1f3c88;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}

if "page" not in st.session_state:
    st.session_state.page = "login"

# =========================
# LOGIN
# =========================
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create Account"):
            st.session_state.page = "create"
            st.rerun()

    with col2:
        if st.button("Forgot Password"):
            if username in st.session_state.users:
                st.info(f"Password: {st.session_state.users[username]}")
            else:
                st.warning("Enter valid username")


def create_account():
    st.title("🆕 Create Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        if new_user in st.session_state.users:
            st.warning("User already exists")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Account created. Please login.")
            st.session_state.page = "login"
            st.rerun()


# ---------------- AUTH ROUTING ----------------
if not st.session_state.logged_in:
    if st.session_state.page == "create":
        create_account()
    else:
        login_page()
    st.stop()

# =========================
# DASHBOARD
# =========================

st.title("📊 Multi-Dataset Fusion Dashboard")

# -------- SIDEBAR --------
st.sidebar.title("📁 Upload Datasets")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.rerun()

# -------- DOMAINS --------
domains = {
    "Education Analytics": ["student", "marks", "roll"],
    "Healthcare Management": ["patient", "medical", "hospital"],
    "E-Commerce & Retail": ["order", "product", "customer"],
    "Banking & Finance": ["account", "transaction", "customer"],
    "HR Management": ["employee", "salary", "department"],
    "Supply Chain": ["shipment", "supplier", "inventory"],
    "Telecommunications": ["subscriber", "call", "network"],
    "Real Estate": ["property", "buyer", "price"],
    "Social Media Analytics": ["user", "post", "engagement"],
    "Manufacturing": ["machine", "batch", "production"]
}

domain = st.selectbox("📂 Select Business Domain", list(domains.keys()))

# -------- DRAG & DROP FILE UPLOAD --------
uploaded_files = st.sidebar.file_uploader(
    "📤 Drag & Drop files here or Click to Browse",
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
# PROCESS FILES
# =========================

if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    # -------- DOMAIN VALIDATION --------
    expected_keywords = domains[domain]
    all_columns = " ".join(df_list[0].columns)

    if not any(keyword in all_columns for keyword in expected_keywords):
        st.error(f"❌ Uploaded datasets do not match selected domain: {domain}")
        st.stop()

    # -------- AUTO DETECT COMMON COLUMNS --------
    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols = common_cols.intersection(set(df.columns))

    if not common_cols:
        st.error("❌ No common join columns detected.")
        st.stop()

    join_column = st.selectbox("🔎 Select Join Column", list(common_cols))
    join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"])

    if st.button("🚀 Merge Datasets"):

        final = df_list[0]
        for df in df_list[1:]:
            final = final.merge(df, on=join_column, how=join_type)

        st.session_state["final_df"] = final
        st.success("Datasets merged successfully!")

# =========================
# AFTER MERGE
# =========================

if "final_df" in st.session_state:

    final = st.session_state["final_df"]

    # -------- CLEANING --------
    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=np.number).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # -------- KPI --------
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    # -------- VISUALS --------
    st.subheader("📈 Visual Analytics")

    numeric_cols = final.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:
        selected = st.selectbox("Select Numeric Column", numeric_cols)

        colA, colB = st.columns(2)

        fig_bar = px.bar(final[selected].value_counts().head(10))
        colA.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(final, names=selected)
        colB.plotly_chart(fig_pie, use_container_width=True)

        fig_line = px.line(final[selected])
        st.plotly_chart(fig_line, use_container_width=True)

        corr = final[numeric_cols].corr()
        fig_heat = px.imshow(corr, text_auto=True)
        st.plotly_chart(fig_heat, use_container_width=True)

    # -------- ML --------
    st.subheader("🤖 Machine Learning")

    if len(numeric_cols) >= 2:
        target = st.selectbox("Target Column", numeric_cols)
        features = final[numeric_cols].drop(columns=[target])

        if st.button("Run Regression"):
            model = LinearRegression()
            model.fit(features, final[target])
            st.success("Regression Model Trained")

        if st.button("Run Clustering"):
            kmeans = KMeans(n_clusters=3, n_init=10)
            final["Cluster"] = kmeans.fit_predict(features)
            st.success("Clustering Completed")
            st.dataframe(final.head())

    # -------- EXPORT --------
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

    st.download_button(
        "Download JSON",
        final.to_json(),
        "final_dataset.json"
    )

else:
    st.info("Upload at least 2 files and merge to begin analysis.")
