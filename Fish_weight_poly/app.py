import streamlit as st
import numpy as np
import pickle
import os

# Set up page
st.set_page_config(page_title="Fish Weight Prediction", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.markdown("Predict weight using measurements: **Length1, Length2, Length3, Height, and Width.**")

# Load model
@st.cache_resource
def load_model():
    model_path = 'Fish_model.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            # Unpacks the [Transformer, Regressor] list in your pkl
            return pickle.load(f)
    return None

model_data = load_model()

if model_data is not None:
    poly, model = model_data[0], model_data[1]
    st.success("✅ Model loaded successfully!")

    # Input fields for all 5 required features
    col1, col2 = st.columns(2)
    with col1:
        l1 = st.number_input("Vertical Length (cm)", min_value=0.0, value=23.2)
        l2 = st.number_input("Diagonal Length (cm)", min_value=0.0, value=25.4)
        l3 = st.number_input("Cross Length (cm)", min_value=0.0, value=30.0)
    with col2:
        h = st.number_input("Height (cm)", min_value=0.0, value=11.5)
        w = st.number_input("Width (cm)", min_value=0.0, value=4.0)

    if st.button("Predict Weight", type="primary"):
        # Create input array
        features = np.array([[l1, l2, l3, h, w]])
        # 1. Polynomial Transform (Degree 2)
        poly_features = poly.transform(features)
        # 2. Linear Prediction
        prediction = model.predict(poly_features)
        
        st.metric("Predicted Weight", f"{max(0, prediction[0]):.2f} grams")
        st.balloons()
else:
    st.error("❌ 'Fish_model.pkl' not found.")
    st.info("Upload the .pkl file to the same folder as this script to enable predictions.")
