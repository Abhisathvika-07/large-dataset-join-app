import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Domain Pie Analytics Dashboard", layout="wide")

st.title("📊 Domain-Based Pie Analytics Dashboard")

# ---------------- DOMAIN LIST ----------------
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

# ---------------- FILE UPLOAD ----------------
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

# ---------------- PIE VISUALIZATION ----------------
if "final_df" in st.session_state:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()

    st.subheader("📊 Domain-Based Pie Chart Insight")

    # ---------------- EDUCATION ----------------
    if domain == "Education Analytics":

        if "grade" in final.columns:
            grade_counts = final["grade"].value_counts().reset_index()
            grade_counts.columns = ["Grade", "Count"]

            fig = px.pie(grade_counts,
                         values="Count",
                         names="Grade",
                         title="Grade Distribution of Students")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the percentage distribution of grades among students, helping identify overall academic performance levels.")

        elif "marks" in final.columns:
            avg_marks = final.groupby("student")["marks"].mean().reset_index()

            fig = px.pie(avg_marks,
                         values="marks",
                         names="student",
                         title="Average Marks Distribution Across Students")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart represents the proportion of total average marks contributed by each student.")

        else:
            st.warning("No marks or grade column found.")

    # ---------------- HEALTHCARE ----------------
    elif domain == "Healthcare Management":

        status_col = None
        for col in final.columns:
            if "status" in col or "recovered" in col or "disease" in col:
                status_col = col
                break

        if status_col:
            status_counts = final[status_col].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig = px.pie(status_counts,
                         values="Count",
                         names="Status",
                         title="Patient Status Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the distribution of patients based on recovery status such as recovered, diseased, or deceased.")

        else:
            st.warning("No patient status column found.")

    # ---------------- E-COMMERCE ----------------
    elif domain == "E-Commerce & Retail":

        if "category" in final.columns:
            category_counts = final["category"].value_counts().reset_index()
            category_counts.columns = ["Category", "Sales Count"]

            fig = px.pie(category_counts,
                         values="Sales Count",
                         names="Category",
                         title="Product Category Sales Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart represents the sales distribution across product categories.")

        else:
            st.warning("No category column found.")

    # ---------------- BANKING ----------------
    elif domain == "Banking & Finance":

        if "type" in final.columns:
            type_counts = final["type"].value_counts().reset_index()
            type_counts.columns = ["Transaction Type", "Count"]

            fig = px.pie(type_counts,
                         values="Count",
                         names="Transaction Type",
                         title="Transaction Type Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the percentage of different transaction types such as deposits and withdrawals.")

        else:
            st.warning("No transaction type column found.")

    # ---------------- HR ----------------
    elif domain == "HR Management":

        if "department" in final.columns:
            dept_counts = final["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Employees"]

            fig = px.pie(dept_counts,
                         values="Employees",
                         names="Department",
                         title="Employee Distribution by Department")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows how employees are distributed across different departments.")

        else:
            st.warning("No department column found.")

    # ---------------- SUPPLY CHAIN ----------------
    elif domain == "Supply Chain":

        if "status" in final.columns:
            status_counts = final["status"].value_counts().reset_index()
            status_counts.columns = ["Shipment Status", "Count"]

            fig = px.pie(status_counts,
                         values="Count",
                         names="Shipment Status",
                         title="Shipment Status Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart displays the proportion of shipments that are delivered, pending, or delayed.")

        else:
            st.warning("No shipment status column found.")

    # ---------------- TELECOM ----------------
    elif domain == "Telecommunications":

        if "plan" in final.columns:
            plan_counts = final["plan"].value_counts().reset_index()
            plan_counts.columns = ["Plan Type", "Subscribers"]

            fig = px.pie(plan_counts,
                         values="Subscribers",
                         names="Plan Type",
                         title="Subscriber Plan Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows how subscribers are distributed across different telecom plans.")

        else:
            st.warning("No plan column found.")

    # ---------------- REAL ESTATE ----------------
    elif domain == "Real Estate":

        if "type" in final.columns:
            type_counts = final["type"].value_counts().reset_index()
            type_counts.columns = ["Property Type", "Count"]

            fig = px.pie(type_counts,
                         values="Count",
                         names="Property Type",
                         title="Property Type Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows the percentage of different property types available.")

        else:
            st.warning("No property type column found.")

    # ---------------- SOCIAL MEDIA ----------------
    elif domain == "Social Media Analytics":

        if "platform" in final.columns:
            platform_counts = final["platform"].value_counts().reset_index()
            platform_counts.columns = ["Platform", "Posts"]

            fig = px.pie(platform_counts,
                         values="Posts",
                         names="Platform",
                         title="Post Distribution by Platform")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart represents how posts are distributed across different social media platforms.")

        else:
            st.warning("No platform column found.")

    # ---------------- MANUFACTURING ----------------
    elif domain == "Manufacturing":

        if "machine" in final.columns:
            machine_counts = final["machine"].value_counts().reset_index()
            machine_counts.columns = ["Machine", "Production Count"]

            fig = px.pie(machine_counts,
                         values="Production Count",
                         names="Machine",
                         title="Production Distribution by Machine")

            st.plotly_chart(fig, use_container_width=True)

            st.write("This pie chart shows how production output is distributed across different machines.")

        else:
            st.warning("No machine column found.")
