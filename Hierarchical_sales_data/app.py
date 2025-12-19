import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.cluster.hierarchy import dendrogram

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Hierarchical Sales Analysis",
    layout="centered"
)

st.title("📊 Hierarchical Sales Data Analysis")
st.write("Visualize and analyze hierarchical clustering on sales data")

# -------------------------------------------------
# Load model
# -------------------------------------------------
@st.cache_resource
def load_pickle():
    with open("hierarchical_sales.pkl", "rb") as f:
        return pickle.load(f)

try:
    model_obj = load_pickle()
    st.success("✅ hierarchical_sales.pkl loaded successfully")
except Exception as e:
    st.error(f"❌ Error loading pickle file: {e}")
    st.stop()

# -------------------------------------------------
# Inspect pickle contents
# -------------------------------------------------
st.subheader("📦 Pickle File Contents")
st.write("Type of loaded object:", type(model_obj))

# Case 1: Dictionary-based pickle
if isinstance(model_obj, dict):
    st.write("Keys found in pickle:", list(model_obj.keys()))

    linkage_matrix = model_obj.get("linkage", None)
    data = model_obj.get("data", None)

# Case 2: Direct linkage matrix
elif isinstance(model_obj, np.ndarray):
    linkage_matrix = model_obj
    data = None

else:
    linkage_matrix = None
    data = None

# -------------------------------------------------
# Dendrogram Visualization
# -------------------------------------------------
st.subheader("🌳 Hierarchical Dendrogram")

if linkage_matrix is not None:
    fig, ax = plt.subplots(figsize=(8, 4))
    dendrogram(linkage_matrix)
    ax.set_title("Sales Hierarchy Dendrogram")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Distance")
    st.pyplot(fig)
else:
    st.warning("⚠️ No linkage matrix found for dendrogram visualization")

# -------------------------------------------------
# Optional: Show sales data
# -------------------------------------------------
if isinstance(data, pd.DataFrame):
    st.subheader("📄 Sales Dataset Preview")
    st.dataframe(data.head())

# -------------------------------------------------
# Info section
# -------------------------------------------------
st.markdown("""
### 🔍 What this app does
- Loads hierarchical sales clustering model
- Displays pickle structure
- Visualizes dendrogram if linkage exists
- Shows dataset preview (if available)

### 📌 Common Use Cases
- Sales region segmentation  
- Product category hierarchy  
- Business decision support  
""")
