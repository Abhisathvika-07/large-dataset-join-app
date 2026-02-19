import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config("Multi Dataset Fusion Platform", layout="wide")

# ==========================
# SESSION STATE INIT
# ==========================
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================
# STYLING
# ==========================
def login_style():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg,#1f2937,#111827);
    }
    h1,label {color:white !important;}
    .block-container {
        background: rgba(255,255,255,0.05);
        padding:2rem;
        border-radius:15px;
    }
    </style>
    """, unsafe_allow_html=True)

def main_style():
    st.markdown("""
    <style>
    .stApp {background-color:#f4f6f9;}
    h1,h2,h3,label {color:#1e293b !important;}
    .block-container {
        background:white;
        padding:2rem;
        border-radius:15px;
        box-shadow:0 6px 18px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================
# LOGIN PAGE
# ==========================
if not st.session_state.logged_in:

    login_style()
    st.title("🔐 Data Fusion Platform Login")

    mode = st.radio("Select Option", ["Login","Create Account","Forgot Password"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if mode == "Login":
        if st.button("Login"):
            if username in st.session_state.users and \
               st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

    elif mode == "Create Account":
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.warning("User already exists")
            else:
                st.session_state.users[username] = password
                st.success("Account created successfully")

    elif mode == "Forgot Password":
        if st.button("Recover Password"):
            if username in st.session_state.users:
                st.success(f"Your password: {st.session_state.users[username]}")
            else:
                st.error("User not found")

# ==========================
# MAIN DASHBOARD
# ==========================
else:

    main_style()

    # ---- SIDEBAR ----
    st.sidebar.title("📂 Upload Datasets")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    uploaded_files = st.sidebar.file_uploader(
        "Upload CSV / Excel / JSON",
        type=["csv","xlsx","json"],
        accept_multiple_files=True
    )

    st.title("📊 Multi-Dataset Fusion Dashboard")

    if uploaded_files and len(uploaded_files) >= 2:

        dfs = []

        for file in uploaded_files:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_json(file)

            dfs.append(df)

        # ---- AUTO DETECT JOIN KEYS ----
        common_cols = set(dfs[0].columns)
        for df in dfs[1:]:
            common_cols &= set(df.columns)

        if not common_cols:
            st.error("No common columns found between files.")
            st.stop()

        join_col = st.selectbox("Select Join Column", list(common_cols))
        join_type = st.selectbox("Join Type", ["inner","left","right","outer"])

        # ---- MERGE ----
        final = dfs[0]
        for df in dfs[1:]:
            final = pd.merge(final, df, on=join_col, how=join_type)

        st.success("Datasets merged successfully!")

        # ---- KPI SECTION ----
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", len(final))
        c2.metric("Columns", len(final.columns))
        c3.metric("Missing Values", final.isnull().sum().sum())

        # ---- DATA CLEANING OPTIONS ----
        st.subheader("🛠 Data Cleaning Options")

        if st.checkbox("Remove Duplicates"):
            final = final.drop_duplicates()

        if st.checkbox("Drop Null Rows"):
            final = final.dropna()

        if st.checkbox("Fill Missing Values"):
            final = final.fillna(0)

        # ---- CHARTS ----
        st.subheader("📈 Visual Insights")

        numeric_cols = final.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:

            selected_col = st.selectbox("Select Numeric Column", numeric_cols)

            col1, col2 = st.columns(2)

            # Bar Chart
            col1.bar_chart(final[selected_col].value_counts().head(10))

            # Pie Chart
            fig, ax = plt.subplots()
            final[selected_col].value_counts().head(5).plot.pie(autopct="%1.1f%%")
            col2.pyplot(fig)

            # Correlation Heatmap
            st.subheader("Correlation Heatmap")
            fig2, ax2 = plt.subplots()
            sns.heatmap(final[numeric_cols].corr(), annot=True, cmap="coolwarm")
            st.pyplot(fig2)

        # ---- DATA PREVIEW ----
        st.subheader("📋 Final Dataset Preview")
        st.dataframe(final.head(100))

        # ---- EXPORT ----
        st.subheader("⬇ Export Data")

        csv = final.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "final_data.csv")

    else:
        st.info("Upload at least 2 files to begin.")

