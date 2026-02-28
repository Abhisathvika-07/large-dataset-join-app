import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Domain Pie Analytics Dashboard", layout="wide")

st.title("📊 Domain-Based Pie Analytics Dashboard")

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

domain = st.selectbox("📂 Select Business Domain", domains)

uploaded_files = st.sidebar.file_uploader(
    "Upload at least 2 related datasets",
    type=["csv"],
    accept_multiple_files=True
)

@st.cache_data
def load_file(file):
    return pd.read_csv(file)

# ---------------- MERGE ----------------
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols &= set(df.columns)

    if common_cols:
        join_column = st.selectbox("Select Join Column", list(common_cols))

        if st.button("Merge Datasets"):
            final = df_list[0]
            for df in df_list[1:]:
                final = final.merge(df, on=join_column, how="inner")

            st.session_state.final_df = final
            st.success("Datasets merged successfully!")
    else:
        st.error("No common columns found.")

# ---------------- SMART FINDER ----------------
def find_column(columns, keywords):
    for col in columns:
        for key in keywords:
            if key in col:
                return col
    return None

# ---------------- VISUALIZATION ----------------
if "final_df" in st.session_state:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()
    columns = final.columns

    st.subheader("📊 Domain-Based Pie Chart Insight")

    # ======================================================
    # EDUCATION
    # ======================================================
    if domain == "Education Analytics":

        grade_col = find_column(columns, ["grade", "result"])
        score_col = find_column(columns, ["mark", "score", "percentage"])

        if grade_col:
            counts = final[grade_col].value_counts().reset_index()
            counts.columns = ["Grade", "Count"]

            fig = px.pie(counts, values="Count", names="Grade",
                         title="Student Grade Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the percentage of students in each grade category, helping evaluate overall academic performance.")

        elif score_col:
            avg_scores = final.groupby(join_column)[score_col].mean().reset_index()

            fig = px.pie(avg_scores,
                         values=score_col,
                         names=join_column,
                         title="Average Score Distribution Among Students")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart represents each student's contribution to the overall average score.")

        else:
            st.warning("No score or grade related column detected.")

    # ======================================================
    # HEALTHCARE
    # ======================================================
    elif domain == "Healthcare Management":

        status_col = find_column(columns, ["status", "recovered", "disease", "outcome"])

        if status_col:
            counts = final[status_col].value_counts().reset_index()
            counts.columns = ["Status", "Count"]

            fig = px.pie(counts, values="Count", names="Status",
                         title="Patient Health Status Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the proportion of patients who are recovered, diseased, or deceased.")

        else:
            st.warning("No patient status column detected.")

    # ======================================================
    # BANKING
    # ======================================================
    elif domain == "Banking & Finance":

        type_col = find_column(columns, ["type", "transaction"])
        if type_col:
            counts = final[type_col].value_counts().reset_index()
            counts.columns = ["Transaction Type", "Count"]

            fig = px.pie(counts, values="Count", names="Transaction Type",
                         title="Transaction Type Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the distribution of different transaction types such as deposits and withdrawals.")
        else:
            st.warning("No transaction type column detected.")

    # ======================================================
    # E-COMMERCE
    # ======================================================
    elif domain == "E-Commerce & Retail":

        category_col = find_column(columns, ["category", "product"])
        if category_col:
            counts = final[category_col].value_counts().reset_index()
            counts.columns = ["Category", "Count"]

            fig = px.pie(counts, values="Count", names="Category",
                         title="Product Category Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the distribution of products across different categories.")
        else:
            st.warning("No product category column detected.")

    # ======================================================
    # HR
    # ======================================================
    elif domain == "HR Management":

        dept_col = find_column(columns, ["department"])
        if dept_col:
            counts = final[dept_col].value_counts().reset_index()
            counts.columns = ["Department", "Employees"]

            fig = px.pie(counts, values="Employees", names="Department",
                         title="Employee Distribution by Department")
            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows how employees are distributed across departments.")
        else:
            st.warning("No department column detected.")

    # ======================================================
    # OTHERS (Simple Fallback)
    # ======================================================
    else:
        cat_cols = final.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            col = cat_cols[0]
            counts = final[col].value_counts().reset_index()
            counts.columns = ["Category", "Count"]

            fig = px.pie(counts, values="Count", names="Category",
                         title=f"{col.title()} Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.write(f"This pie chart shows the distribution of different {col} categories.")
        else:
            st.warning("No categorical column found for visualization.")
