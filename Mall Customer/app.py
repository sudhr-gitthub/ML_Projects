import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Mall Customer Segmentation",
    layout="wide"
)

st.title("🛍️ Mall Customer Segmentation – Hierarchical Clustering")

# --------------------------------------------------
# Load preprocessed data
# --------------------------------------------------
@st.cache_data
def load_data():
    return joblib.load("mall_customers.pkl")

try:
    df = load_data()
except Exception as e:
    st.error("❌ Failed to load mall_customers.pkl")
    st.stop()

st.subheader("📊 Preprocessed Customer Data")
st.dataframe(df.head(), use_container_width=True)

# --------------------------------------------------
# Cluster assignment using saved centroids
# --------------------------------------------------
st.subheader("🔮 Predict Customer Cluster")

age = st.slider("Age", 18, 70, 30)
income = st.slider("Annual Income (k$)", 10, 150, 60)
score = st.slider("Spending Score (1–100)", 1, 100, 50)

# Load centroids
@st.cache_resource
def load_centroids():
    return joblib.load("mall_customer_centroids.pkl")

try:
    centroids = load_centroids()
except Exception:
    st.error("❌ Centroid file not found (mall_customer_centroids.pkl)")
    st.stop()

if st.button("Predict Cluster"):
    user = np.array([[age, income, score]])
    distances = ((centroids - user) ** 2).sum(axis=1)
    cluster = distances.argmin()
    st.success(f"🧠 Customer belongs to **Cluster {cluster}**")

# --------------------------------------------------
# Optional visualization
# --------------------------------------------------
st.subheader("📈 Cluster Visualization")

fig, ax = plt.subplots()
ax.scatter(df.iloc[:, 0], df.iloc[:, 1], s=30)
ax.set_xlabel("Feature 1")
ax.set_ylabel("Feature 2")
st.pyplot(fig)

st.markdown("---")
st.caption("Hierarchical Clustering | Streamlit App")
