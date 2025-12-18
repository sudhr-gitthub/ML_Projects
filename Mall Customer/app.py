import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🛍️ Mall Customer Segmentation – Hierarchical Clustering")

@st.cache_data
def load_object():
    return joblib.load("mall_customer_hier.pkl")

try:
    obj = load_object()
except Exception as e:
    st.error("❌ Failed to load mall_customer_hier.pkl")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# Detect object type
# --------------------------------------------------
st.subheader("📦 Loaded Object Info")
st.write("Type:", type(obj))

# --------------------------------------------------
# CASE 1: Pandas DataFrame
# --------------------------------------------------
if isinstance(obj, pd.DataFrame):
    df = obj
    st.subheader("📊 Preprocessed Customer Data")
    st.dataframe(df.head(), use_container_width=True)

    if df.shape[1] >= 2:
        fig, ax = plt.subplots()
        ax.scatter(df.iloc[:, 0], df.iloc[:, 1], alpha=0.6)
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])
        st.pyplot(fig)

# --------------------------------------------------
# CASE 2: NumPy array
# --------------------------------------------------
elif isinstance(obj, np.ndarray):
    st.subheader("📊 NumPy Data Loaded")
    st.write("Shape:", obj.shape)
    st.dataframe(pd.DataFrame(obj).head())

# --------------------------------------------------
# CASE 3: Dictionary
# --------------------------------------------------
elif isinstance(obj, dict):
    st.subheader("📦 Dictionary Keys")
    st.write(obj.keys())

# --------------------------------------------------
# UNKNOWN
# --------------------------------------------------
else:
    st.warning("⚠️ Unsupported object type. Cannot visualize.")

st.markdown("---")
st.caption("Hierarchical Clustering | Streamlit App")
