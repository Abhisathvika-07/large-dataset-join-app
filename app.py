import streamlit as st
import pandas as pd
import io

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="Enterprise AI Data Fusion", layout="wide")

# ------------------------------
# SESSION STATE INIT
# ------------------------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ------------------------------
# LOGIN PAGE STYLING
# ------------------------------
def login_background():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #eef2f3, #d9e4f5);
        }

        h1, h2, h3, label, p {
            color: #1f2937 !important;
        }

        .stTextInput > div > div > input {
            background-color: white;
            color: black;
        }

        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
        }
        </style>
    """, unsafe_allow_html=True)


# ------------------------------
# MAIN PAGE STYLING
# ------------------------------
def main_background():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1558494949-ef010cbdcc31");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .block-container {
            background: rgba(255,255,255,0.92);
            padding: 30px;
            border-radius: 15px;
        }

        h1, h2, h3, label {
            color: #111827 !important;
        }

        .stMetric {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 10px;
        }

        .stButton > button {
            background-color: #1d4ed8;
            color: white;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)


# ------------------------------
# CREATE ACCOUNT PAGE
# ------------------------------
def create_account():
    login_background()

    st.title("🆕 Create Account")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Register"):
        if new_user in st.session_state.users:
            st.error("User already exists")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Account created successfully!")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ------------------------------
# LOGIN PAGE
# ------------------------------
def login():
    login_background()

    st.title("🔐 Enterprise Secure Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.write("---")
    if st.button("Create Account"):
        st.session_state.page = "create"
        st.rerun()

# ------------------------------
# MAIN APPLICATION
# ------------------------------
def main_app():
    main_background()

    st.title("🚀 Enterprise AI Data Fusion & Analytics Platform")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

    st.sidebar.header("Upload Datasets (CSV, Excel, JSON)")

    uploaded_files = st.sidebar.file_uploader(
        "Upload Files",
        type=["csv", "xlsx", "json"],
        accept_multiple_files=True
    )

    if uploaded_files:
        dataframes = []

        for file in uploaded_files:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.name.endswith(".json"):
                df = pd.read_json(file)
            dataframes.append(df)

        # Auto detect join column
        common_columns = set(dataframes[0].columns)
        for df in dataframes[1:]:
            common_columns &= set(df.columns)

        if common_columns:
            join_col = st.selectbox("Select Join Column", list(common_columns))
            join_type = st.selectbox("Select Join Type", ["inner", "left", "right", "outer"])

            final = dataframes[0]
            for df in dataframes[1:]:
                final = pd.merge(final, df, on=join_col, how=join_type)

            st.success("Datasets merged successfully!")

            # KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", final.shape[0])
            col2.metric("Columns", final.shape[1])
            col3.metric("Missing Values", final.isnull().sum().sum())

            st.subheader("Preview")
            st.dataframe(final.head(100), use_container_width=True)

            # EXPORT OPTIONS
            st.subheader("Export Data")

            colA, colB, colC = st.columns(3)

            # CSV
            csv = final.to_csv(index=False).encode()
            colA.download_button("Download CSV", csv, "data.csv", "text/csv")

            # Excel
            excel_buffer = io.BytesIO()
            final.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)
            colB.download_button(
                "Download Excel",
                excel_buffer,
                "data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # JSON
            json_data = final.to_json(orient="records").encode()
            colC.download_button("Download JSON", json_data, "data.json", "application/json")

        else:
            st.error("No common column found to join.")

    else:
        st.info("Upload multiple datasets to begin analysis.")

# ------------------------------
# ROUTER
# ------------------------------
if st.session_state.page == "login":
    login()

elif st.session_state.page == "create":
    create_account()

elif st.session_state.page == "main":
    main_app()

