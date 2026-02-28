import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Multi-Dataset Fusion Dashboard", layout="wide")

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
.stApp { background-color: #0f1c2e; }
section[data-testid="stSidebar"] { background-color: #0b1625; }
h1, h2, h3, h4, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "final_df" not in st.session_state:
    st.session_state.final_df = None

# =========================
# DOMAIN SELECTION
# =========================
domains = [
    "Education Analytics",
    "Healthcare Management",
    "E-Commerce & Retail",
    "Banking & Finance",
    "HR Management",
    "Supply Chain",
    "Telecommunications",
    "Real Estate",
    "Social Media Analytics",
    "Manufacturing"
]

st.title("📊 Multi-Dataset Fusion Dashboard")

domain = st.selectbox("📂 Select Business Domain", domains)

# =========================
# FILE UPLOAD
# =========================
uploaded_files = st.sidebar.file_uploader(
    "Upload at least 2 related datasets",
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
# MERGING
# =========================
if uploaded_files and len(uploaded_files) >= 2:
    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols &= set(df.columns)

    if common_cols:
        join_column = st.selectbox("Select Join Column", list(common_cols))
        join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"])

        if st.button("Merge Datasets"):
            final = df_list[0]
            for df in df_list[1:]:
                final = final.merge(df, on=join_column, how=join_type)

            st.session_state.final_df = final
            st.success("Datasets merged successfully!")
    else:
        st.error("No common columns found to merge.")

# =========================
# AFTER MERGE
# =========================
if st.session_state.final_df is not None:

    final = st.session_state.final_df
    columns = final.columns

    st.subheader("🧹 Data Cleaning")

    if st.checkbox("Remove Duplicates"):
        final = final.drop_duplicates()

    if st.checkbox("Drop Null Rows"):
        final = final.dropna()

    if st.checkbox("Normalize Numeric Columns"):
        scaler = MinMaxScaler()
        num_cols = final.select_dtypes(include=["number"]).columns
        final[num_cols] = scaler.fit_transform(final[num_cols])

    # KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", final.shape[0])
    col2.metric("Columns", final.shape[1])
    col3.metric("Missing Values", final.isnull().sum().sum())

    st.subheader("📊 Domain Based Visual Analytics")

    # ==========================================================
    # EDUCATION
    # ==========================================================
    if domain == "Education Analytics":
        if "marks" in columns:
            st.metric("Average Marks", round(final["marks"].mean(), 2))

            fig_bar = px.bar(final, x="student" if "student" in columns else final.index,
                             y="marks", title="Student Marks")
            st.plotly_chart(fig_bar, use_container_width=True)

            fig_line = px.line(final, y="marks", markers=True,
                               title="Marks Trend")
            st.plotly_chart(fig_line, use_container_width=True)

            if "grade" in columns:
                grade_counts = final["grade"].value_counts().reset_index()
                grade_counts.columns = ["Grade", "Count"]
                fig_pie = px.pie(grade_counts, values="Count",
                                 names="Grade",
                                 title="Grade Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================================
    # HEALTHCARE
    # ==========================================================
    elif domain == "Healthcare Management":
        if "hospital" in columns:
            hospital_counts = final["hospital"].value_counts().reset_index()
            hospital_counts.columns = ["Hospital", "Patients"]

            fig_bar = px.bar(hospital_counts, x="Hospital", y="Patients",
                             title="Patients per Hospital")
            st.plotly_chart(fig_bar, use_container_width=True)

        if "disease" in columns:
            disease_counts = final["disease"].value_counts().reset_index()
            disease_counts.columns = ["Disease", "Count"]

            fig_pie = px.pie(disease_counts, values="Count",
                             names="Disease",
                             title="Disease Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================================
    # E-COMMERCE
    # ==========================================================
    elif domain == "E-Commerce & Retail":
        if "product" in columns:
            product_counts = final["product"].value_counts().reset_index()
            product_counts.columns = ["Product", "Orders"]

            fig_bar = px.bar(product_counts, x="Product", y="Orders",
                             title="Orders per Product")
            st.plotly_chart(fig_bar, use_container_width=True)

        if "price" in columns:
            fig_line = px.line(final, y="price", title="Price Trend")
            st.plotly_chart(fig_line, use_container_width=True)

    # ==========================================================
    # BANKING
    # ==========================================================
    elif domain == "Banking & Finance":
        if "account" in columns:
            acc_counts = final["account"].value_counts().reset_index()
            acc_counts.columns = ["Account", "Transactions"]

            fig_bar = px.bar(acc_counts, x="Account", y="Transactions",
                             title="Transactions per Account")
            st.plotly_chart(fig_bar, use_container_width=True)

        if "amount" in columns:
            fig_line = px.line(final, y="amount",
                               title="Transaction Amount Trend")
            st.plotly_chart(fig_line, use_container_width=True)

    # ==========================================================
    # HR
    # ==========================================================
    elif domain == "HR Management":
        if "department" in columns:
            dept_counts = final["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Employees"]

            fig_bar = px.bar(dept_counts, x="Department", y="Employees",
                             title="Employees per Department")
            st.plotly_chart(fig_bar, use_container_width=True)

        if "salary" in columns:
            fig_line = px.line(final, y="salary",
                               title="Salary Trend")
            st.plotly_chart(fig_line, use_container_width=True)

    # ==========================================================
    # SUPPLY CHAIN
    # ==========================================================
    elif domain == "Supply Chain":
        if "supplier" in columns:
            sup_counts = final["supplier"].value_counts().reset_index()
            sup_counts.columns = ["Supplier", "Shipments"]

            fig_bar = px.bar(sup_counts, x="Supplier", y="Shipments",
                             title="Shipments per Supplier")
            st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # TELECOM
    # ==========================================================
    elif domain == "Telecommunications":
        if "subscriber" in columns:
            sub_counts = final["subscriber"].value_counts().reset_index()
            sub_counts.columns = ["Subscriber", "Count"]

            fig_bar = px.bar(sub_counts, x="Subscriber", y="Count",
                             title="Subscribers")
            st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # REAL ESTATE
    # ==========================================================
    elif domain == "Real Estate":
        if "property" in columns:
            prop_counts = final["property"].value_counts().reset_index()
            prop_counts.columns = ["Property", "Count"]

            fig_bar = px.bar(prop_counts, x="Property", y="Count",
                             title="Property Listings")
            st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # SOCIAL MEDIA
    # ==========================================================
    elif domain == "Social Media Analytics":
        if "post" in columns:
            post_counts = final["post"].value_counts().reset_index()
            post_counts.columns = ["Post", "Count"]

            fig_bar = px.bar(post_counts, x="Post", y="Count",
                             title="Post Engagement")
            st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # MANUFACTURING
    # ==========================================================
    elif domain == "Manufacturing":
        if "machine" in columns:
            mach_counts = final["machine"].value_counts().reset_index()
            mach_counts.columns = ["Machine", "Production"]

            fig_bar = px.bar(mach_counts, x="Machine", y="Production",
                             title="Production per Machine")
            st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.info("Upload at least 2 related files to begin analysis.")
