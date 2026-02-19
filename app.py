import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Enterprise Data Platform", layout="wide")

# -----------------------------
# CLEAN PROFESSIONAL BACKGROUND
# -----------------------------
st.markdown("""
<style>

/* Full background */
.stApp {
    background: url("https://images.unsplash.com/photo-1492724441997-5dc865305da7") no-repeat center center fixed;
    background-size: cover;
}

/* Remove default white container */
.block-container {
    padding-top: 2rem;
    background: transparent;
}

/* Centered Login Card */
.login-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px;
    border-radius: 15px;
    width: 400px;
    margin: auto;
    margin-top: 120px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
}

/* Dashboard container */
.dashboard-container {
    background: rgba(255,255,255,0.92);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
}

/* Buttons */
.stButton>button {
    background-color: #0A3D62;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

def login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.title("🔐 Secure Enterprise Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.auth:
    login()
    st.stop()

# -----------------------------
# DASHBOARD
# -----------------------------
st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

st.title("📊 Enterprise Multi-Dataset Join Platform")

dataset_type = st.selectbox(
    "Select Dataset Domain",
    [
        "Education","E-Commerce","Healthcare",
        "Employee Management","Finance",
        "Retail","Banking","Telecom",
        "Insurance","Manufacturing"
    ]
)

join_type = st.selectbox(
    "Select Join Type",
    ["inner","left","right","outer"]
)

st.sidebar.header("Upload CSV Files")
file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id",
    "Finance": "account_id",
    "Retail": "product_id",
    "Banking": "customer_id",
    "Telecom": "subscriber_id",
    "Insurance": "policy_id",
    "Manufacturing": "machine_id"
}

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    join_column = join_keys[dataset_type]

    if join_column in df1.columns and join_column in df2.columns:

        final = pd.merge(df1, df2, on=join_column, how=join_type)

        st.success(f"Joined using {join_type.upper()} on {join_column}")

        col1, col2 = st.columns(2)
        col1.metric("Total Rows", len(final))
        col2.metric("Total Columns", len(final.columns))

        st.subheader("Preview")
        st.dataframe(final.head(50), use_container_width=True)

        csv = final.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "merged.csv")

        st.subheader("Analytics")

        numeric_cols = final.select_dtypes(include=["int64","float64"]).columns

        if len(numeric_cols) > 0:
            selected = st.selectbox("Select Numeric Column", numeric_cols)

            fig = px.bar(final[selected].value_counts().head(10))
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"Column {join_column} not found")

else:
    st.info("Upload both datasets")

st.markdown('</div>', unsafe_allow_html=True)

