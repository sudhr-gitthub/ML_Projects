import streamlit as st
import pickle
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Hierarchical Sales Analysis")

st.title("📊 Hierarchical Sales Data Analysis")

MODEL_FILE = "hierarchical_sales.pkl"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sudhr-gitthub/ML_Projects/main/Hierarchical_sales_data/hierarchical_sales.pkl"

# -------------------------------------------------
# Download model if not exists
# -------------------------------------------------
def download_model():
    if not os.path.exists(MODEL_FILE):
        st.info("⬇️ Downloading model from GitHub...")
        response = requests.get(GITHUB_RAW_URL)
        with open(MODEL_FILE, "wb") as f:
            f.write(response.content)

download_model()

# -------------------------------------------------
# Load pickle
# -------------------------------------------------
try:
    with open(MODEL_FILE, "rb") as f:
        model_obj = pickle.load(f)
    st.success("✅ Model loaded successfully")
except Exception as e:
    st.error(f"❌ Error loading pickle file: {e}")
    st.stop()

# -------------------------------------------------
# Dendrogram
# -------------------------------------------------
st.subheader("🌳 Hierarchical Dendrogram")

if isinstance(model_obj, dict) and "linkage" in model_obj:
    fig, ax = plt.subplots(figsize=(8, 4))
    dendrogram(model_obj["linkage"])
    st.pyplot(fig)
elif isinstance(model_obj, np.ndarray):
    fig, ax = plt.subplots(figsize=(8, 4))
    dendrogram(model_obj)
    st.pyplot(fig)
else:
    st.warning("⚠️ No linkage matrix found")
