import streamlit as st
import numpy as np
import pickle
import os

# Page configuration
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.markdown("Predict weight using **numeric dimensions**: Length1, Length2, Length3, Height, and Width.")

# 1. Loading Logic with Path Diagnostics
@st.cache_resource
def load_model():
    model_path = "Fish_model.pkl"
    
    # Check if file exists
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as f:
                # Unpacks the [PolynomialFeatures, LinearRegression] tuple 
                return pickle.load(f)
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return None
    return None

model_data = load_model()

# 2. User Interface and Numeric Inputs
if model_data is not None:
    poly, model = model_data[0], model_data[1]
    st.success("✅ Model loaded successfully!")

    st.subheader("Enter Measurements (Numbers Only)")
    col1, col2 = st.columns(2)
    
    with col1:
        # st.number_input ensures inputs are treated as numbers
        l1 = st.number_input("Vertical Length (Length1)", min_value=0.0, value=23.2, format="%.2f")
        l2 = st.number_input("Diagonal Length (Length2)", min_value=0.0, value=25.4, format="%.2f")
        l3 = st.number_input("Cross Length (Length3)", min_value=0.0, value=30.0, format="%.2f")
    
    with col2:
        h = st.number_input("Height", min_value=0.0, value=11.5, format="%.2f")
        w = st.number_input("Width", min_value=0.0, value=4.0, format="%.2f")

    if st.button("Predict Weight", type="primary"):
        # Features array 
        features = np.array([[l1, l2, l3, h, w]])
        
        # 1. Transform features 
        poly_features = poly.transform(features)
        
        # 2. Predict weight [cite: 2]
        prediction = model.predict(poly_features)
        
        # Show result (Model intercept is approx 256.40) [cite: 2]
        st.metric("Predicted Weight", f"{max(0, prediction[0]):.2f} grams")
        st.balloons()
else:
    # Diagnostic section to help you fix the error
    st.error("❌ 'Fish_model.pkl' not found!")
    
    with st.expander("🛠️ Debug Folder Contents"):
        st.write(f"**Current Working Directory:** `{os.getcwd()}`")
        st.write("**Files detected in this folder:**")
        st.write(os.listdir("."))
    
    st.info("💡 **How to fix:** Ensure 'Fish_model.pkl' is uploaded to the same folder as this script on GitHub or your computer.")

st.divider()
st.caption("Model scikit-learn version: 1.6.1 | Expected Features: Length1, Length2, Length3, Height, Width")
