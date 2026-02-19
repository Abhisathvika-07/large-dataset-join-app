import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Data Fusion Platform", layout="wide")

# -------------------------------
# SESSION STATE INIT
# -------------------------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"


# -------------------------------
# BACKGROUND FUNCTION
# -------------------------------
def set_background(image_url=None, gradient=None):
    if image_url:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("{image_url}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            .block-container {{
                background-color: rgba(0,0,0,0.55);
                padding: 2rem;
                border-radius: 15px;
            }}

            h1, h2, h3, label {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    elif gradient:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: {gradient};
                height: 100vh;
            }}

            .block-container {{
                background-color: rgba(0,0,0,0.5);
                padding: 2rem;
                border-radius: 15px;
            }}

            h1, h2, h3, label {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


# ===============================
# LOGIN PAGE
# ===============================
if not st.session_state.logged_in:

    # Animated dark gradient login background
    set_background(
        gradient="linear-gradient(135deg, #141E30, #243B55)"
    )

    st.title("🔐 Secure Login Portal")

    choice = st.radio("Select Option", ["Login", "Create Account"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users and \
               st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            if new_user in st.session_state.users:
                st.warning("User already exists")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Account created successfully! Please login.")
                st.session_state.page = "login"

# ===============================
# MAIN DASHBOARD
# ===============================
else:

    # Your grey texture image
    set_background("background_main.jpg")

    st.title("📊 Multi-Dataset Data Fusion Dashboard")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.subheader("Upload Datasets (CSV, Excel, JSON)")

    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["csv", "xlsx", "json"],
        accept_multiple_files=True
    )

    if uploaded_files:

        dfs = []

        for file in uploaded_files:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_json(file)

            dfs.append(df)

        # Auto detect common columns
        common_cols = set(dfs[0].columns)
        for df in dfs[1:]:
            common_cols = common_cols.intersection(df.columns)

        if common_cols:
            join_column = st.selectbox(
                "Select Join Column",
                list(common_cols)
            )

            join_type = st.selectbox(
                "Select Join Type",
                ["inner", "left", "right", "outer"]
            )

            final = dfs[0]
            for df in dfs[1:]:
                final = pd.merge(final, df,
                                 on=join_column,
                                 how=join_type)

            st.success("Datasets merged successfully!")

            # KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", len(final))
            col2.metric("Columns", len(final.columns))
            col3.metric("Missing Values",
                        final.isnull().sum().sum())

            # Insights
            st.subheader("Summary Statistics")
            st.dataframe(final.describe())

            # Data Preview
            st.subheader("Data Preview")
            st.dataframe(final.head(100))

            # Export
            st.subheader("Export Data")
            csv = final.to_csv(index=False).encode()
            st.download_button("Download CSV",
                               csv,
                               "final_data.csv",
                               "text/csv")
        else:
            st.error("No common columns found for join.")

