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
def load_model():
    model_path = "Fish_model.pkl"
    if not os.path.exists(model_path):
        st.error(f"❌ File Not Found: Please ensure '{model_path}' is in the same folder as this script.")
        return None, None
    
    with open(model_path, "rb") as f:
        # The pickle contains [PolynomialFeatures, LinearRegression] 
        poly, model = pickle.load(f)
    return poly, model

poly, model = load_model()

if poly is not None:
    st.success("✅ Model version 1.6.1 loaded successfully")

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
        # Order: Length1, Length2, Length3, Height, Width 
        input_features = np.array([[l1, l2, l3, h, w]])
        
        # Apply the Polynomial transformation 
        input_poly = poly.transform(input_features)
        
        # Generate prediction [cite: 2]
        prediction = model.predict(input_poly)
        
        st.metric(label="Estimated Fish Weight", value=f"{prediction[0]:.2f} grams")
        st.balloons()

    st.divider()
    st.info("Note: This model requires Length1, Length2, Length3, Height, and Width.")
