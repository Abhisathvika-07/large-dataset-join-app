import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(page_title="Enterprise Data Platform", layout="wide")

# ---------------------------------------
# PROFESSIONAL BACKGROUND IMAGE
# ---------------------------------------
st.markdown("""
<style>

/* MAIN APP BACKGROUND */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1551288049-bebda4e38f71");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Glass container effect */
.block-container {
    background: rgba(255,255,255,0.90);
    padding: 2rem;
    border-radius: 15px;
    animation: fadeIn 1.2s ease-in;
}

/* Fade Animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Professional Buttons */
.stButton>button {
    background-color: #0A3D62;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}

/* Login Page Background */
.login-bg {
    background-image: url("https://images.unsplash.com/photo-1542744173-8e7e53415bb0");
    background-size: cover;
    background-position: center;
    padding: 60px;
    border-radius: 20px;
    animation: fadeIn 1.5s ease-in;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# SIMPLE LOGIN SYSTEM
# ---------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.markdown('<div class="login-bg">', unsafe_allow_html=True)
    st.title("🔐 Secure Enterprise Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    login()
    st.stop()

# ---------------------------------------
# MAIN DASHBOARD
# ---------------------------------------
st.title("📊 Enterprise Multi-Dataset Join Platform")

# Domain Categories
dataset_type = st.selectbox(
    "Select Dataset Domain",
    [
        "Education",
        "E-Commerce",
        "Healthcare",
        "Employee Management",
        "Finance",
        "Banking",
        "Retail",
        "Telecom",
        "Supply Chain",
        "Insurance",
        "Manufacturing"
    ]
)

join_type = st.selectbox(
    "Select Join Type",
    ["inner", "left", "right", "outer"]
)

# Sidebar Upload
st.sidebar.header("Upload CSV Files")
file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])

# Join Key Mapping
join_keys = {
    "Education": "student_id",
    "E-Commerce": "customer_id",
    "Healthcare": "patient_id",
    "Employee Management": "employee_id",
    "Finance": "account_id",
    "Banking": "customer_id",
    "Retail": "product_id",
    "Telecom": "subscriber_id",
    "Supply Chain": "order_id",
    "Insurance": "policy_id",
    "Manufacturing": "machine_id"
}

if file1 and file2:

    with st.spinner("Processing enterprise data..."):
        df1 = pd.read_csv(file1, low_memory=False)
        df2 = pd.read_csv(file2, low_memory=False)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        join_column = join_keys[dataset_type]

        if join_column in df1.columns and join_column in df2.columns:

            final = pd.merge(df1, df2, on=join_column, how=join_type)

            st.success(f"Successfully joined using {join_type.upper()} join on {join_column}")

            # KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(final))
            col2.metric("Total Columns", len(final.columns))
            col3.metric("Missing Values", final.isnull().sum().sum())

            st.divider()

            st.subheader("📄 Data Preview")
            st.dataframe(final.head(100), use_container_width=True)

            # Download
            csv = final.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download Merged File", csv, "merged.csv", "text/csv")

            # ---------------- VISUALIZATION ----------------
            st.subheader("📈 Analytics Dashboard")

            numeric_cols = final.select_dtypes(include=["int64","float64"]).columns

            if len(numeric_cols) > 0:

                selected_col = st.selectbox("Select Numeric Column", numeric_cols)

                colA, colB = st.columns(2)

                with colA:
                    st.write("Bar Chart")
                    fig_bar = px.bar(final[selected_col].value_counts().head(10))
                    st.plotly_chart(fig_bar, use_container_width=True)

                with colB:
                    st.write("Pie Chart")
                    fig_pie = px.pie(final, names=selected_col)
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.write("Line Chart")
                fig_line = px.line(final[selected_col].head(50))
                st.plotly_chart(fig_line, use_container_width=True)

            else:
                st.info("No numeric columns available for visualization.")

        else:
            st.error(f"Column '{join_column}' not found in both datasets.")

else:
    st.info("Upload both datasets to begin analysis.")

