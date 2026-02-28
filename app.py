import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Domain Analytics Dashboard", layout="wide")

st.title("📊 Domain-Based Analytics Dashboard")

# =========================
# DOMAIN KEYWORDS (STRICT VALIDATION)
# =========================
domain_keywords = {
    "Education Analytics": ["student", "mark", "score", "grade"],
    "Healthcare Management": ["patient", "hospital", "disease", "status"],
    "E-Commerce & Retail": ["product", "category", "sales", "price"],
    "Banking & Finance": ["account", "transaction", "amount", "balance"]
}

domain = st.selectbox("📂 Select Business Domain", list(domain_keywords.keys()))

# =========================
# FILE UPLOAD
# =========================
uploaded_files = st.sidebar.file_uploader(
    "Upload related datasets",
    type=["csv"],
    accept_multiple_files=True
)

@st.cache_data
def load_file(file):
    return pd.read_csv(file)

# =========================
# MERGE + VALIDATION
# =========================
if uploaded_files and len(uploaded_files) >= 2:

    df_list = [load_file(f) for f in uploaded_files]
    df_list = [df.rename(columns=lambda x: x.strip().lower()) for df in df_list]

    # ---- STRICT DOMAIN VALIDATION ----
    all_columns = []
    for df in df_list:
        all_columns.extend(df.columns.tolist())

    expected_keywords = domain_keywords[domain]

    match_count = sum(
        1 for keyword in expected_keywords
        for col in all_columns
        if keyword in col
    )

    if match_count < 2:
        st.error(f"❌ Uploaded dataset does NOT match selected domain: {domain}")
        st.stop()

    # ---- FIND COMMON COLUMN ----
    common_cols = set(df_list[0].columns)
    for df in df_list[1:]:
        common_cols &= set(df.columns)

    if not common_cols:
        st.error("❌ No common columns found to merge.")
        st.stop()

    join_column = st.selectbox("Select Join Column", list(common_cols))

    if st.button("Merge Datasets"):

        final = df_list[0]
        for df in df_list[1:]:
            final = final.merge(df, on=join_column, how="inner")

        st.session_state.final_df = final
        st.success("Datasets merged successfully!")

# =========================
# DOMAIN VISUALIZATION
# =========================
if "final_df" in st.session_state:

    final = st.session_state.final_df
    final.columns = final.columns.str.lower()

    st.subheader("📊 Domain Insight")

    def find_column(keywords):
        for col in final.columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    # ==========================================================
    # BANKING
    # ==========================================================
    if domain == "Banking & Finance":

        amount_col = find_column(["amount", "balance"])
        type_col = find_column(["type", "transaction"])

        if amount_col and type_col:
            summary = final.groupby(type_col)[amount_col].sum().reset_index()

            fig = px.pie(summary,
                         names=type_col,
                         values=amount_col,
                         title="Transaction Amount Distribution by Type")

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "This chart shows how total money is distributed across different transaction types "
                "such as deposits, withdrawals, or transfers. Larger segments indicate higher financial activity."
            )

    # ==========================================================
    # E-COMMERCE
    # ==========================================================
    elif domain == "E-Commerce & Retail":

        revenue_col = find_column(["sales", "price", "amount"])
        category_col = find_column(["category", "product"])

        if revenue_col and category_col:
            summary = final.groupby(category_col)[revenue_col].sum().reset_index()

            fig = px.pie(summary,
                         names=category_col,
                         values=revenue_col,
                         title="Revenue Contribution by Product Category")

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "This pie chart shows which product categories generate the most revenue. "
                "Bigger slices represent higher total sales."
            )

    # ==========================================================
    # EDUCATION
    # ==========================================================
    elif domain == "Education Analytics":

        grade_col = find_column(["grade", "result"])
        score_col = find_column(["mark", "score"])

        if grade_col:
            summary = final[grade_col].value_counts().reset_index()
            summary.columns = ["Grade", "Count"]

            fig = px.pie(summary,
                         names="Grade",
                         values="Count",
                         title="Student Grade Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "This pie chart represents the distribution of students across different grades, "
                "helping evaluate overall academic performance."
            )

        elif score_col:
            avg_score = final[score_col].mean()
            st.metric("Average Score", round(avg_score, 2))

    # ==========================================================
    # HEALTHCARE
    # ==========================================================
    elif domain == "Healthcare Management":

        status_col = find_column(["status", "outcome", "recovered", "disease"])

        if status_col:
            summary = final[status_col].value_counts().reset_index()
            summary.columns = ["Health Status", "Count"]

            fig = px.pie(summary,
                         names="Health Status",
                         values="Count",
                         title="Patient Health Status Distribution")

            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "This chart shows the proportion of patients who are recovered, under treatment, "
                "or deceased. It provides insight into overall healthcare outcomes."
            )

else:
    st.info("Upload at least 2 related datasets to begin.")
