import streamlit as st
import numpy as np
import pickle

# Configuration
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.markdown("""
Predict the weight of a fish based on its physical dimensions using a **Polynomial Linear Regression** model.
""")

# Load the model components from the uploaded pickle file
# The file contains the PolynomialFeatures transformer and the LinearRegression model 
@st.cache_resource
def load_model():
    with open("Fish_model.pkl", "rb") as f:
        # The pickle structure stores the transformer (poly) and the regressor (model) [cite: 1, 2]
        poly, model = pickle.load(f)
    return poly, model

try:
    poly, model = load_model()
    st.success("✅ Model version 1.6.1 loaded successfully ")
except Exception as e:
    st.error(f"Error loading model: {e}")

st.divider()

# Input section using the specific feature names from the model 
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
    # Arrange features in the order expected by the model 
    input_features = np.array([[l1, l2, l3, h, w]])
    
    # Apply the Polynomial transformation 
    input_poly = poly.transform(input_features)
    
    # Generate prediction 
    prediction = model.predict(input_poly)
    
    # The intercept_ for this model is approximately 256.40 
    st.metric(label="Estimated Fish Weight", value=f"{prediction[0]:.2f} grams")
    st.balloons()

st.divider()
st.info("Note: This model uses Length1, Length2, Length3, Height, and Width as inputs.")
