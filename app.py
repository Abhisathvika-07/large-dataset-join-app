import streamlit as st
import pandas as pd

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Enterprise Data Join Platform", layout="wide")

# -------------------------------------------------------
# SESSION STATE FOR LOGIN
# -------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

# -------------------------------------------------------
# LOGIN PAGE STYLING
# -------------------------------------------------------
def login_background():
    st.markdown("""
    <style>
    .stApp {
        background-image: 
        linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
        url("https://images.unsplash.com/photo-1492724441997-5dc865305da7");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    header, #MainMenu, footer {
        visibility: hidden;
    }

    h1, h2, h3, label {
        color: white !important;
    }

    .stTextInput > div > div > input {
        background-color: #111827 !important;
        color: white !important;
    }

    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }

    .stButton button:hover {
        background-color: #1e40af;
    }

    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# MAIN PAGE STYLING
# -------------------------------------------------------
def main_background():
    st.markdown("""
    <style>
    .stApp {
        background-image: 
        linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
        url("https://images.unsplash.com/photo-1551288049-bebda4e38f71");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    header, #MainMenu, footer {
        visibility: hidden;
    }

    h1, h2, h3, label {
        color: white !important;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #111827 !important;
        color: white !important;
    }

    .stButton button {
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }

    .stButton button:hover {
        background-color: #059669;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# LOGIN / REGISTER PAGE
# -------------------------------------------------------
if not st.session_state.logged_in:

    login_background()

    st.markdown("## 🔐 Secure Enterprise Login")

    option = st.radio("Select Option", ["Login", "Create Account"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            if username in st.session_state.users and \
               st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.warning("User already exists")
            else:
                st.session_state.users[username] = password
                st.success("Account Created! Please login.")

# -------------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------------
else:

    main_background()

    st.title("📊 Enterprise Multi-Dataset Join Platform")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Dataset Domains
    dataset_type = st.selectbox(
        "Select Dataset Domain",
        [
            "Education",
            "E-Commerce",
            "Healthcare",
            "Employee Management",
            "Banking",
            "Retail",
            "Telecommunications",
            "Logistics",
            "Manufacturing",
            "Insurance"
        ]
    )

    # Join Type
    join_type = st.selectbox(
        "Select Join Type",
        ["inner", "left", "right", "outer"]
    )

    st.sidebar.header("Upload CSV Files")

    file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
    file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

    join_keys = {
        "Education": "student_id",
        "E-Commerce": "customer_id",
        "Healthcare": "patient_id",
        "Employee Management": "employee_id",
        "Banking": "account_id",
        "Retail": "product_id",
        "Telecommunications": "subscriber_id",
        "Logistics": "shipment_id",
        "Manufacturing": "machine_id",
        "Insurance": "policy_id"
    }

    if file1 and file2:

        with st.spinner("Processing datasets..."):

            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)

            df1.columns = df1.columns.str.strip()
            df2.columns = df2.columns.str.strip()

            join_column = join_keys[dataset_type]

            if join_column in df1.columns and join_column in df2.columns:

                final = pd.merge(df1, df2, on=join_column, how=join_type)

                st.success(
                    f"Joined using {join_type.upper()} join on '{join_column}'"
                )

                col1, col2 = st.columns(2)
                col1.metric("Total Rows", len(final))
                col2.metric("Total Columns", len(final.columns))

                st.subheader("Preview (First 100 Rows)")
                st.dataframe(final.head(100), use_container_width=True)

                csv = final.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "⬇ Download Merged Dataset",
                    data=csv,
                    file_name="merged_dataset.csv",
                    mime="text/csv"
                )

                # Visualization
                numeric_cols = final.select_dtypes(
                    include=["int64", "float64"]
                ).columns

                if len(numeric_cols) > 0:
                    selected_col = st.selectbox(
                        "Select Column for Visualization",
                        numeric_cols
                    )

                    st.bar_chart(final[selected_col].value_counts().head(10))
                    st.line_chart(final[selected_col].head(50))
                else:
                    st.info("No numeric columns available.")

            else:
                st.error(
                    f"Required column '{join_column}' not found in both files."
                )

    else:
        st.info("Please upload both CSV files to begin.")

