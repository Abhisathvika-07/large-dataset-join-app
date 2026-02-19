import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Enterprise Data Join Platform",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# GLOBAL CORPORATE STYLING
# -------------------------------------------------
st.markdown("""
<style>

/* ===== FULL BACKGROUND ===== */
.stApp {
    background: linear-gradient(
        rgba(5, 20, 40, 0.92),
        rgba(5, 20, 40, 0.92)
    ),
    url("https://images.unsplash.com/photo-1492724441997-5dc865305da7");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* ===== LOGIN CARD ===== */
.login-box {
    background: rgba(255, 255, 255, 0.08);
    padding: 45px;
    border-radius: 15px;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 40px rgba(0,0,0,0.6);
    animation: fadeIn 1s ease-in-out;
}

/* ===== DASHBOARD CARD ===== */
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 12px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    animation: fadeUp 0.8s ease-in-out;
}

/* ===== TITLES ===== */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    color: #00C6FF;
    margin-top: 20px;
}

/* ===== KPI STYLE ===== */
.kpi {
    font-size: 28px;
    font-weight: bold;
    color: #00C6FF;
}

/* ===== ANIMATIONS ===== */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

@keyframes fadeUp {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# AUTHENTICATION SYSTEM
# -------------------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = {
    "admin": hash_password("admin123"),
    "manager": hash_password("manager123")
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
if not st.session_state.authenticated:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">🔐 Secure Enterprise Login</div>', unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username] == hash_password(password):
                st.session_state.authenticated = True
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# -------------------------------------------------
# MAIN DASHBOARD
# -------------------------------------------------
st.markdown('<div class="main-title">📊 Enterprise Multi-Dataset Join Platform</div>', unsafe_allow_html=True)

# Attractive Banner Image
st.image(
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    use_container_width=True
)

# Dataset Type Selection
dataset_type = st.selectbox(
    "Select Dataset Category",
    ["Education", "E-Commerce", "Healthcare", "Employee Management",
     "Banking", "Finance", "Retail", "Manufacturing",
     "Logistics", "Telecom", "Insurance", "Government"]
)

# Join Type
join_type = st.selectbox(
    "Select Join Type",
    ["inner", "left", "right", "outer"]
)

# File Upload
st.sidebar.header("Upload CSV Files")
file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id",
    "Banking": "account_id",
    "Finance": "transaction_id",
    "Retail": "order_id",
    "Manufacturing": "product_id",
    "Logistics": "shipment_id",
    "Telecom": "subscriber_id",
    "Insurance": "policy_id",
    "Government": "citizen_id"
}

# -------------------------------------------------
# PROCESS FILES
# -------------------------------------------------
if file1 and file2:

    with st.spinner("Processing large datasets... ⏳"):

        df1 = pd.read_csv(file1, low_memory=False)
        df2 = pd.read_csv(file2, low_memory=False)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        join_column = join_keys[dataset_type]

        if join_column in df1.columns and join_column in df2.columns:

            final = pd.merge(df1, df2, on=join_column, how=join_type)

            st.success(f"Joined using {join_type.upper()} on '{join_column}'")

            # KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='card'><div class='kpi'>{len(final)}</div>Total Rows</div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><div class='kpi'>{len(final.columns)}</div>Total Columns</div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><div class='kpi'>{final.memory_usage().sum()//1024} KB</div>Memory Usage</div>", unsafe_allow_html=True)

            # Preview
            st.markdown('<div class="section-title">Preview Data</div>', unsafe_allow_html=True)
            st.dataframe(final.head(100), use_container_width=True)

            # Download
            csv = final.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download Merged Dataset", csv, "merged_dataset.csv", "text/csv")

            # ----------------------
            # VISUALIZATION
            # ----------------------
            st.markdown('<div class="section-title">Data Visualization</div>', unsafe_allow_html=True)

            numeric_cols = final.select_dtypes(include=["int64", "float64"]).columns

            if len(numeric_cols) > 0:

                selected_col = st.selectbox("Select Column for Analysis", numeric_cols)

                colA, colB = st.columns(2)

                with colA:
                    fig_bar = px.bar(final[selected_col].value_counts().head(10),
                                     title="Bar Chart")
                    st.plotly_chart(fig_bar, use_container_width=True)

                with colB:
                    fig_pie = px.pie(final, names=selected_col, title="Pie Chart")
                    st.plotly_chart(fig_pie, use_container_width=True)

                fig_line = px.line(final[selected_col], title="Line Chart Trend")
                st.plotly_chart(fig_line, use_container_width=True)

            else:
                st.info("No numeric columns found.")

        else:
            st.error(f"Column '{join_column}' not found in both datasets")

else:
    st.info("Upload both CSV files to begin.")
