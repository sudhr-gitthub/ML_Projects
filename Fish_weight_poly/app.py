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
    
    # Check if the file exists to prevent the Errno 2 error
    if not os.path.exists(model_path):
        st.error(f"❌ **File Not Found:** The app cannot find '{model_path}'.")
        st.info("💡 **Solution:** Ensure 'Fish_model.pkl' is uploaded to the same folder as this script on GitHub or your local machine.")
        return None, None
    
    try:
        with open(model_path, "rb") as f:
            # The pickle contains [PolynomialFeatures, LinearRegression] sequentially
            poly, model = pickle.load(f)
        return poly, model
    except Exception as e:
        st.error(f"❌ **Error Loading Model:** {e}")
        return None, None

# Initialize the model components 
poly, model = load_model()

if poly is not None and model is not None:
    st.success("✅ Model loaded successfully (v1.6.1)")

    st.divider()

    # Input section based on model features: Length1, Length2, Length3, Height, Width 
    
    
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
        # Create input array in the exact order required by the model 
        input_data = np.array([[l1, l2, l3, h, w]])
        
        # 1. Apply the Polynomial transformation 
        input_poly = poly.transform(input_data)
        
        # 2. Generate prediction using the linear model 
        prediction = model.predict(input_poly)
        
        # Display the result (The model has a specific intercept of approx 256.40) 
        st.metric(label="Estimated Fish Weight", value=f"{prediction[0]:.2f} grams")
        st.balloons()

st.divider()
st.info("Note: This model uses Length1, Length2, Length3, Height, and Width as inputs.")
