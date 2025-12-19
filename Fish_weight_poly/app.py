import streamlit as st
import numpy as np
import pickle
import os

# Configuration
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.markdown("""
Predict the weight of a fish based on its physical dimensions using a **Polynomial Linear Regression** model.
""")

# Load the model components
@st.cache_resource
def load_model(uploaded_file=None):
    if uploaded_file is not None:
        # Load from the user's upload
        data = pickle.load(uploaded_file)
        return data[0], data[1] # poly, model
    
    model_path = "Fish_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            # The pickle contains [PolynomialFeatures, LinearRegression] 
            data = pickle.load(f)
            # Depending on how it was saved, it's likely a list/tuple
            if isinstance(data, (list, tuple)):
                return data[0], data[1]
            return None, None
    return None, None

# Try loading from local file first
poly, model = load_model()

# If local file is missing, provide an uploader
if poly is None:
    st.warning("⚠️ **Fish_model.pkl** not found in the project folder.")
    uploaded_file = st.file_uploader("Please upload 'Fish_model.pkl' to continue", type="pkl")
    if uploaded_file:
        poly, model = load_model(uploaded_file)
        st.success("✅ Model uploaded and loaded successfully!")

if poly is not None and model is not None:
    st.success("✅ Model version 1.6.1 ready") [cite: 1]

    st.divider()

    # Input section based on model metadata 
    col1, col2 = st.columns(2)

    with col1:
        l1 = st.number_input("Vertical Length (Length1) (cm)", value=23.2, min_value=0.0)
        l2 = st.number_input("Diagonal Length (Length2) (cm)", value=25.4, min_value=0.0)
        l3 = st.number_input("Cross Length (Length3) (cm)", value=30.0, min_value=0.0)

    with col2:
        h = st.number_input("Height (cm)", value=11.5, min_value=0.0)
        w = st.number_input("Width (cm)", value=4.0, min_value=0.0)

    # Prediction Logic
    if st.button("Predict Weight", type="primary"):
        # Features: Length1, Length2, Length3, Height, Width 
        input_features = np.array([[l1, l2, l3, h, w]])
        
        # 1. Apply Polynomial transformation
        input_poly = poly.transform(input_features)
        
        # 2. Generate prediction
        prediction = model.predict(input_poly)
        
        # Display results
        st.metric(label="Estimated Fish Weight", value=f"{prediction[0]:.2f} grams")
        st.balloons()

st.divider()
st.info("Note: This model uses Length1, Length2, Length3, Height, and Width as inputs.") [cite: 1]
