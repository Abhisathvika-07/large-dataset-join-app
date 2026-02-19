import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -----------------------------
# REMOVE STREAMLIT HEADER
# -----------------------------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -----------------------------
# LOGIN STATE
# -----------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False


# =============================
# LOGIN PAGE
# =============================
def login_page():

    st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1522071820081-009f0129c71c")
        no-repeat center center fixed;
        background-size: cover;
    }

    .login-box {
        background: rgba(0, 0, 0, 0.75);
        padding: 40px;
        border-radius: 15px;
        width: 400px;
        margin: auto;
        margin-top: 150px;
        color: white;
        text-align: center;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.5);
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🔐 Enterprise Secure Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.markdown('</div>', unsafe_allow_html=True)


# =============================
# DASHBOARD PAGE
# =============================
def dashboard():

    st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1492724441997-5dc865305da7")
        no-repeat center center fixed;
        background-size: cover;
    }

    .main-container {
        background: rgba(255,255,255,0.92);
        padding: 30px;
        border-radius: 15px;
        margin-top: 40px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.3);
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

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

            st.dataframe(final.head(50), use_container_width=True)

            csv = final.to_csv(index=False).encode()
            st.download_button("Download CSV", csv, "merged.csv")

            numeric_cols = final.select_dtypes(include=["int64","float64"]).columns
            if len(numeric_cols) > 0:
                selected = st.selectbox("Select Numeric Column", numeric_cols)
                fig = px.bar(final[selected].value_counts().head(10))
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.error(f"Column {join_column} not found")

    st.markdown('</div>', unsafe_allow_html=True)


# =============================
# ROUTING
# =============================
if not st.session_state.auth:
    login_page()
else:
    dashboard()

