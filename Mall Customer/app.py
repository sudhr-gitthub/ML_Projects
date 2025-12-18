import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🛍️ Mall Customer Segmentation – Hierarchical Clustering")

# --------------------------------------------------
# Load data safely
# --------------------------------------------------
@st.cache_data
def load_data():
    return joblib.load("mall_customer_hier.pkl")

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ mall_customer_hier.pkl not found in repository")
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to load pickle file: {e}")
    st.stop()

# --------------------------------------------------
# Display data
# --------------------------------------------------
st.subheader("📊 Preprocessed Customer Data")
st.dataframe(df.head(), use_container_width=True)

# --------------------------------------------------
# Simple visualization (Cloud-safe)
# --------------------------------------------------
st.subheader("📈 Customer Distribution")

if df.shape[1] >= 2:
    fig, ax = plt.subplots()
    ax.scatter(df.iloc[:, 0], df.iloc[:, 1], alpha=0.6)
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    st.pyplot(fig)
else:
    st.warning("Not enough features to plot.")

st.markdown("---")
st.caption("Hierarchical Clustering | Streamlit App")
