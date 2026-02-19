import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Enterprise AI Data Fusion Platform", layout="wide")

st.title("🚀 Enterprise AI Data Fusion & Analytics Platform")

# ===============================
# CACHED FILE LOADER
# ===============================
@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)
    else:
        return None

# ===============================
# FILE UPLOADER
# ===============================
st.sidebar.header("📂 Upload Datasets")
uploaded_files = st.sidebar.file_uploader(
    "Upload Multiple Files (CSV, Excel, JSON)",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

if uploaded_files:

    dataframes = []
    for file in uploaded_files:
        df = load_file(file)
        if df is not None:
            df.columns = df.columns.str.strip()
            dataframes.append(df)

    if len(dataframes) >= 2:

        # ===============================
        # AUTO DETECT COMMON COLUMNS
        # ===============================
        common_cols = list(set(dataframes[0].columns)
                           .intersection(*[set(df.columns) for df in dataframes[1:]]))

        st.subheader("🔗 Join Configuration")

        if common_cols:
            join_column = st.selectbox("Select Join Column", common_cols)
            join_type = st.selectbox("Select Join Type", ["inner", "left", "right", "outer"])
        else:
            st.error("No common columns found between datasets.")
            st.stop()

        # ===============================
        # MERGE ALL FILES
        # ===============================
        final = dataframes[0]
        for df in dataframes[1:]:
            final = final.merge(df, on=join_column, how=join_type)

        st.success("Datasets merged successfully!")

        # ===============================
        # DATA CLEANING OPTIONS
        # ===============================
        st.subheader("🧹 Data Cleaning Options")

        col1, col2, col3, col4 = st.columns(4)

        if col1.checkbox("Remove Duplicates"):
            final = final.drop_duplicates()

        if col2.checkbox("Drop Null Rows"):
            final = final.dropna()

        if col3.checkbox("Fill Missing Values"):
            final = final.fillna(final.mean(numeric_only=True))

        if col4.checkbox("Normalize Numeric Columns"):
            scaler = StandardScaler()
            numeric_cols = final.select_dtypes(include=np.number).columns
            final[numeric_cols] = scaler.fit_transform(final[numeric_cols])

        # ===============================
        # KPI DASHBOARD
        # ===============================
        st.subheader("📊 KPI Dashboard")

        k1, k2, k3 = st.columns(3)

        k1.metric("Total Rows", len(final))
        k2.metric("Total Columns", len(final.columns))
        k3.metric("Missing Values",
                  int(final.isnull().sum().sum()))

        # ===============================
        # DATA INSIGHTS
        # ===============================
        st.subheader("🔎 Automatic Data Insights")

        st.write("### 📌 Summary Statistics")
        st.dataframe(final.describe())

        st.write("### 📌 Top 5 Categories (Categorical Columns)")
        cat_cols = final.select_dtypes(include="object").columns
        for col in cat_cols[:3]:
            st.write(f"Top values in **{col}**")
            st.write(final[col].value_counts().head())

        st.write("### 📌 Missing Values %")
        missing_percent = (final.isnull().sum() / len(final)) * 100
        st.dataframe(missing_percent)

        # ===============================
        # CORRELATION HEATMAP
        # ===============================
        numeric_cols = final.select_dtypes(include=np.number)

        if len(numeric_cols.columns) > 1:
            st.subheader("📈 Correlation Heatmap")
            corr = numeric_cols.corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto")
            st.plotly_chart(fig, use_container_width=True)

        # ===============================
        # AI GENERATED SUMMARY
        # ===============================
        st.subheader("🤖 AI Generated Summary")

        summary_text = f"""
        The merged dataset contains {len(final)} rows and {len(final.columns)} columns.
        The dataset shows highest variation in numeric attributes.
        The most frequent categorical value appears in '{cat_cols[0]}' column
        with value '{final[cat_cols[0]].value_counts().idxmax()}'.
        """
        st.info(summary_text)

        # ===============================
        # ML SECTION
        # ===============================
        st.subheader("🧠 Machine Learning Module")

        ml_option = st.selectbox(
            "Select ML Task",
            ["None", "Regression", "Classification", "Clustering"]
        )

        if ml_option != "None":

            if len(numeric_cols.columns) >= 2:

                target = st.selectbox("Select Target Column", numeric_cols.columns)
                features = numeric_cols.drop(columns=[target])

                if ml_option == "Regression":
                    model = LinearRegression()
                    model.fit(features, numeric_cols[target])
                    preds = model.predict(features)
                    st.success("Regression model trained successfully!")

                elif ml_option == "Classification":
                    model = RandomForestClassifier()
                    y = pd.cut(numeric_cols[target], bins=3, labels=[0,1,2])
                    model.fit(features, y)
                    st.success("Classification model trained!")

                elif ml_option == "Clustering":
                    model = KMeans(n_clusters=3)
                    clusters = model.fit_predict(features)
                    final["Cluster"] = clusters
                    st.success("Clustering completed!")

            else:
                st.warning("Not enough numeric columns for ML.")

        # ===============================
        # EXPORT OPTIONS
        # ===============================
        st.subheader("⬇ Export Data")

        col1, col2, col3 = st.columns(3)

        col1.download_button(
            "Download CSV",
            final.to_csv(index=False),
            "final_dataset.csv",
            "text/csv"
        )

        col2.download_button(
            "Download Excel",
            final.to_excel("temp.xlsx", index=False),
            "final_dataset.xlsx"
        )

        col3.download_button(
            "Download JSON",
            final.to_json(orient="records"),
            "final_dataset.json"
        )

        # ===============================
        # FINAL DATA PREVIEW
        # ===============================
        st.subheader("📋 Final Dataset Preview")
        st.dataframe(final.head(200), use_container_width=True)

    else:
        st.warning("Please upload at least 2 files.")

else:
    st.info("Upload datasets to begin analysis.")

