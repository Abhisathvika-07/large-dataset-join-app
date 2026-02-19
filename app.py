import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise Data Platform", layout="wide")

# =============================
# LOGIN BACKGROUND (ANIMATED)
# =============================
def login_background():
    st.markdown("""
    <style>
    header, #MainMenu, footer {visibility: hidden;}

    body {
        margin: 0;
        padding: 0;
    }

    /* Animated professional background */
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c1c1c);
        background-size: 400% 400%;
        animation: gradientMove 12s ease infinite;
    }

    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .login-box {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(15px);
        padding: 50px;
        border-radius: 20px;
        width: 420px;
        margin: auto;
        margin-top: 120px;
        box-shadow: 0px 0px 40px rgba(0,0,0,0.6);
        color: white;
        animation: fadeIn 1s ease-in-out;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(30px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stTextInput input {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 8px;
    }

    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }

    </style>
    """, unsafe_allow_html=True)



# =============================
# MAIN DASHBOARD BACKGROUND
# =============================
def dashboard_background():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1508780709619-79562169bc64");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .main-container {
        background: rgba(0,0,0,0.75);
        padding: 30px;
        border-radius: 15px;
    }

    h1, h2, h3, label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.logged_in:

    login_background()

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Enterprise Secure Login")

    option = st.radio("", ["Login", "Create Account"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            if username in st.session_state.users and \
               st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.warning("User already exists")
            else:
                st.session_state.users[username] = password
                st.success("Account created successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

# =============================
# DASHBOARD PAGE
# =============================
else:

    dashboard_background()

    st.title("📊 Enterprise Multi-Dataset Join Platform")

    st.sidebar.title("Upload CSV Files")

    file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
    file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

    dataset_type = st.selectbox(
        "Select Dataset Domain",
        ["Education", "E-Commerce", "Healthcare", "Finance",
         "Retail", "Marketing", "Banking", "HR Analytics"]
    )

    join_type = st.selectbox(
        "Select Join Type",
        ["inner", "left", "right", "outer"]
    )

    join_keys = {
        "Education": "student_id",
        "E-Commerce": "customer_id",
        "Healthcare": "patient_id",
        "Finance": "account_id",
        "Retail": "product_id",
        "Marketing": "campaign_id",
        "Banking": "account_id",
        "HR Analytics": "employee_id"
    }

    if file1 and file2:

        with st.spinner("Processing large datasets..."):
            df1 = pd.read_csv(file1, low_memory=False)
            df2 = pd.read_csv(file2, low_memory=False)

            join_column = join_keys[dataset_type]

            if join_column in df1.columns and join_column in df2.columns:

                final = pd.merge(df1, df2, on=join_column, how=join_type)

                st.success("Datasets joined successfully!")

                # KPI CARDS
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rows", len(final))
                col2.metric("Total Columns", len(final.columns))
                col3.metric("Null Values", final.isnull().sum().sum())

                st.subheader("Preview Data")
                st.dataframe(final.head(100), use_container_width=True)

                csv = final.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Merged Dataset",
                    csv,
                    "merged_dataset.csv",
                    "text/csv"
                )

                # CHARTS
                numeric_cols = final.select_dtypes(include=["int64", "float64"]).columns

                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("Select Column for Chart", numeric_cols)

                    colA, colB = st.columns(2)

                    with colA:
                        fig_bar = px.bar(
                            final[selected_col].value_counts().head(10),
                            title="Bar Chart"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

                    with colB:
                        fig_pie = px.pie(
                            final,
                            names=selected_col,
                            title="Pie Chart"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                    fig_line = px.line(
                        final[selected_col].head(50),
                        title="Line Chart Trend"
                    )
                    st.plotly_chart(fig_line, use_container_width=True)

                else:
                    st.info("No numeric columns available for charts.")

            else:
                st.error(f"Column '{join_column}' not found in both datasets.")

    else:
        st.info("Upload both CSV files to begin.")



