import streamlit as st
import pickle
import numpy as np
from sklearn.metrics import pairwise_distances_argmin

# ---------------------------------------------------
# Load trained objects
# ---------------------------------------------------
@st.cache_resource
def load_model():
    with open("mall_customer_hier.pkl", "rb") as f:
        data = pickle.load(f)
    return data

data = load_model()

# EXPECTED STRUCTURE:
# data = {
#   "centroids": np.array([...]),
# }

centroids = data["centroids"]

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.set_page_config(page_title="Mall Customer Segmentation", page_icon="🛍️")

st.title("🛍️ Mall Customer Segmentation")
st.write("Assign a new customer to the nearest cluster")

# ---------------------------------------------------
# Inputs
# ---------------------------------------------------
age = st.slider("Age", 18, 70, 30)
income = st.slider("Annual Income (k$)", 10, 150, 60)
score = st.slider("Spending Score (1–100)", 1, 100, 50)

# ---------------------------------------------------
# Prediction
# ---------------------------------------------------
if st.button("Predict Cluster"):
    user = np.array([[age, income, score]])

    cluster = pairwise_distances_argmin(user, centroids)[0]

    st.success(f"🧠 Customer belongs to **Cluster {cluster}**")

st.markdown("---")
st.caption("Hierarchical Clustering | Streamlit App")
