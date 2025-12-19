import streamlit as st
import numpy as np
import pickle
import os

# Page layout
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.write("Enter the physical dimensions of the fish below to predict its weight in grams.")

# Function to load the model
@st.cache_resource
def load_model():
    model_path = "Fish_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            # Your model file contains: (PolynomialFeatures, LinearRegression)
            data = pickle.load(f)
            return data[0], data[1]
    return None, None

# Load model components
poly, model = load_model()

if poly is not None:
    st.success("✅ Model loaded successfully!")
    
    st.subheader("Numeric Measurements")
    
    # Create two columns for a better layout
    col1, col2 = st.columns(2)
    
    with col1:
        l1 = st.number_input("Vertical Length (cm)", min_value=0.0, value=23.2, format="%.2f")
        l2 = st.number_input("Diagonal Length (cm)", min_value=0.0, value=25.4, format="%.2f")
        l3 = st.number_input("Cross Length (cm)", min_value=0.0, value=30.0, format="%.2f")
    
    with col2:
        h = st.number_input("Height (cm)", min_value=0.0, value=11.5, format="%.2f")
        w = st.number_input("Width (cm)", min_value=0.0, value=4.0, format="%.2f")

    if st.button("Predict Weight", type="primary"):
        # Put inputs into a 2D numpy array
        input_data = np.array([[l1, l2, l3, h, w]])
        
        # 1. Expand to polynomial features
        poly_features = poly.transform(input_data)
        
        # 2. Predict using the regression model
        prediction = model.predict(poly_features)
        
        # Display results
        weight = max(0, prediction[0]) # Weight cannot be negative
        st.metric(label="Predicted Fish Weight", value=f"{weight:.2f} grams")
        st.balloons()

else:
    st.error("❌ **Fish_model.pkl** not found!")
    st.info("Make sure the file 'Fish_model.pkl' is in the same folder as this app.py file.")

st.divider()
st.info("Note: This model requires all 5 numeric inputs (Length1, Length2, Length3, Height, Width).")
