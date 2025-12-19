import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Hierarchical Sales Data", layout="centered")
st.title("📊 Hierarchical Sales Data Analysis")

# -------------------------------------------------
# Download pickle from GitHub (if not exists)
# -------------------------------------------------
MODEL_FILE = "hierarchical_sales.pkl"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sudhr-gitthub/ML_Projects/main/Hierarchical_sales_data/hierarchical_sales.pkl"

if not os.path.exists(MODEL_FILE):
    st.info("⬇️ Downloading sales data...")
    response = requests.get(GITHUB_RAW_URL)
    with open(MODEL_FILE, "wb") as f:
        f.write(response.content)

# -------------------------------------------------
# Load pickle
# -------------------------------------------------
with open(MODEL_FILE, "rb") as f:
    data = pickle.load(f)

st.success("✅ Sales data loaded successfully")

# -------------------------------------------------
# Ensure DataFrame
# -------------------------------------------------
if not isinstance(data, pd.DataFrame):
    st.error("❌ Pickle does not contain a DataFrame")
    st.stop()

# -------------------------------------------------
# Display table
# -------------------------------------------------
st.subheader("📄 Sales Data Table")
st.dataframe(data)

# -------------------------------------------------
# Column selection
# -------------------------------------------------
st.subheader("📈 Hierarchical Sales Graph")

numeric_cols = data.select_dtypes(include="number").columns.tolist()
group_cols = data.select_dtypes(exclude="number").columns.tolist()

if len(numeric_cols) == 0 or len(group_cols) == 0:
    st.warning("⚠️ Not enough columns for hierarchy plotting")
    st.stop()

group_col = st.selectbox("Select Hierarchy Level", group_cols)
value_col = st.selectbox("Select Sales Column", numeric_cols)

# -------------------------------------------------
# Aggregate & Plot
# -------------------------------------------------
agg_data = data.groupby(group_col)[value_col].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 4))
agg_data.plot(kind="bar", ax=ax)
ax.set_title(f"{value_col} by {group_col}")
ax.set_ylabel(value_col)
ax.set_xlabel(group_col)

st.pyplot(fig)
