import streamlit as st
import pickle
import numpy as np

# ---------------------------------------------------
# Load the trained hierarchical clustering model
# ---------------------------------------------------
@st.cache_resource
def load_model():
    with open("mall_customer_hier.pkl", "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.set_page_config(
    page_title="Mall Customer Segmentation",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ Mall Customer Segmentation App")
st.write("Predict the **customer cluster** using Hierarchical Clustering")

# ---------------------------------------------------
# User Inputs
# ---------------------------------------------------
age = st.slider("Age", 18, 70, 30)
annual_income = st.slider("Annual Income (k$)", 10, 150, 60)
spending_score = st.slider("Spending Score (1–100)", 1, 100, 50)

# ---------------------------------------------------
# Prediction
# ---------------------------------------------------
if st.button("Predict Customer Cluster"):
    input_data = np.array([[age, annual_income, spending_score]])

    cluster = model.fit_predict(input_data)[0]

    st.success(f"🧠 Predicted Customer Cluster: **Cluster {cluster}**")

    # Optional explanation
    st.info(
        "Clusters help businesses understand customer behavior for "
        "targeted marketing and personalized offers."
    )

# ---------------------------------------------------
# Footer
# ---------------------------------------------------
st.markdown("---")
st.caption("Developed using Streamlit & Scikit-learn")
