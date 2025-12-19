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
    try:
        if uploaded_file is not None:
            # Load from the user's manual upload
            data = pickle.load(uploaded_file)
            return data[0], data[1]
        
        model_path = "Fish_model.pkl"
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                # The pickle contains [PolynomialFeatures, LinearRegression]
                data = pickle.load(f)
                return data[0], data[1]
    except Exception as e:
        st.error(f"Error unpickling model: {e}")
    return None, None

# Try to load automatically or via uploader
uploaded_file = None
if not os.path.exists("Fish_model.pkl"):
    st.warning("⚠️ **Fish_model.pkl** not found in project folder.")
    uploaded_file = st.file_uploader("Upload 'Fish_model.pkl' to enable prediction", type="pkl")

poly, model = load_model(uploaded_file)

# Only show inputs and prediction button if model is loaded
if poly is not None and model is not None:
    st.success("✅ Model (v1.6.1) loaded and ready!")
    
    st.subheader("Enter Fish Measurements")
    col1, col2 = st.columns(2)

    with col1:
        l1 = st.number_input("Vertical Length (Length1) (cm)", value=23.2, min_value=0.0)
        l2 = st.number_input("Diagonal Length (Length2) (cm)", value=25.4, min_value=0.0)
        l3 = st.number_input("Cross Length (Length3) (cm)", value=30.0, min_value=0.0)

    with col2:
        h = st.number_input("Height (cm)", value=11.5, min_value=0.0)
        w = st.number_input("Width (cm)", value=4.0, min_value=0.0)

    if st.button("Predict Weight", type="primary"):
        # Model expects: Length1, Length2, Length3, Height, Width
        input_data = np.array([[l1, l2, l3, h, w]])
        
        # 1. Polynomial transformation
        input_poly = poly.transform(input_data)
        
        # 2. Linear Prediction
        prediction = model.predict(input_poly)
        
        st.metric(label="Predicted Weight", value=f"{max(0, prediction[0]):.2f} grams")
        st.balloons()
else:
    st.info("Please ensure 'Fish_model.pkl' is present to see the measurement inputs.")

st.divider()
st.caption("Model features: Length1, Length2, Length3, Height, Width")
