import streamlit as st
import pickle
import numpy as np
from sklearn.metrics import pairwise_distances_argmin

# ---------------------------------------------------
# Load model & training data
# ---------------------------------------------------
@st.cache_resource
def load_assets():
    with open("mall_customer_hier.pkl", "rb") as f:
        assets = pickle.load(f)

    return assets

assets = load_assets()

# EXPECTED STRUCTURE:
# assets = {
#   "model": trained_model,
#   "X_train": training_data,
#   "labels": cluster_labels
# }

model = assets["model"]
X_train = assets["X_train"]
labels = assets["labels"]

# ---------------------------------------------------
# Compute cluster centroids
# ---------------------------------------------------
def compute_centroids(X, labels):
    centroids = []
    for label in np.unique(labels):
        centroids.append(X[labels == label].mean(axis=0))
    return np.array(centroids)

centroids = compute_centroids(X_train, labels)

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.set_page_config(
    page_title="Mall Customer Segmentation",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ Mall Customer Segmentation (Hierarchical)")
st.write("Assign a customer to the nearest cluster")

# ---------------------------------------------------
# User Inputs
# ---------------------------------------------------
age = st.slider("Age", 18, 70, 30)
income = st.slider("Annual Income (k$)", 10, 150, 60)
score = st.slider("Spending Score (1–100)", 1, 100, 50)

# ---------------------------------------------------
# Predict Cluster
# ---------------------------------------------------
if st.button("Predict Cluster"):
    user_data = np.array([[age, income, score]])

    cluster = pairwise_distances_argmin(user_data, centroids)[0]

    st.success(f"🎯 Predicted Customer Cluster: **Cluster {cluster}**")

st.markdown("---")
st.caption("Hierarchical Clustering | Streamlit App")
