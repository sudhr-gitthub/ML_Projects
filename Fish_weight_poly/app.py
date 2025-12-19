import streamlit as st
import numpy as np
import pickle
import os

# Set up page configuration
st.set_page_config(page_title="Fish Weight Prediction", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.markdown("""
Predict the weight of a fish based on its physical dimensions using a **Polynomial Linear Regression** model.
""")

# Function to load model
@st.cache_resource
def load_model():
    model_path = 'Fish_model.pkl'
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                # The model is saved as a list: [PolynomialFeatures, LinearRegression]
                model_data = pickle.load(f)
                return model_data
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return None
    return None

# Load model
model_data = load_model()

if model_data is not None:
    # Unpack the transformer and the model
    poly = model_data[0]
    model = model_data[1]
    
    st.success("✅ Model loaded successfully!")
    
    st.subheader("Enter Fish Measurements")
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        l1 = st.number_input("Vertical Length (Length1) (cm)", min_value=0.0, value=23.2, step=0.1)
        l2 = st.number_input("Diagonal Length (Length2) (cm)", min_value=0.0, value=25.4, step=0.1)
        l3 = st.number_input("Cross Length (Length3) (cm)", min_value=0.0, value=30.0, step=0.1)
    
    with col2:
        height = st.number_input("Height (cm)", min_value=0.0, value=11.5, step=0.1)
        width = st.number_input("Width (cm)", min_value=0.0, value=4.0, step=0.1)

    # Prediction logic
    if st.button("Predict Weight", type="primary"):
        # Features must be in order: Length1, Length2, Length3, Height, Width
        input_data = np.array([[l1, l2, l3, height, width]])
        
        # 1. Apply the Polynomial transformation
        input_poly = poly.transform(input_data)
        
        # 2. Predict the weight
        prediction = model.predict(input_poly)
        
        # Display the result
        st.metric(label="Estimated Fish Weight", value=f"{max(0, prediction[0]):.2f} grams")
        st.balloons()
else:
    st.error("❌ 'Fish_model.pkl' not found.")
    st.info("Please ensure 'Fish_model.pkl' is in the same folder as this script.")

st.divider()
st.info("Note: This model uses Length1, Length2, Length3, Height, and Width as inputs.")
