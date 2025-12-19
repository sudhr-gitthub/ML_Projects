import streamlit as st
import numpy as np
import pickle
import os

# Page layout
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.write("Enter numeric dimensions to predict weight.")

# Function to load the model
@st.cache_resource
def load_model():
    model_path = "Fish_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            # Your pkl contains: [PolynomialFeatures, LinearRegression]
            data = pickle.load(f)
            return data[0], data[1]
    return None, None

# Load model components
poly, model = load_model()

if poly is not None:
    st.success("✅ Model loaded successfully!")
    
    # Input section: Using number_input ensures data is numeric
    col1, col2 = st.columns(2)
    
    with col1:
        # These 5 features are required by your model: Length1, Length2, Length3, Height, Width
        l1 = st.number_input("Vertical Length (Length1)", min_value=0.0, value=23.2)
        l2 = st.number_input("Diagonal Length (Length2)", min_value=0.0, value=25.4)
        l3 = st.number_input("Cross Length (Length3)", min_value=0.0, value=30.0)
    
    with col2:
        h = st.number_input("Height", min_value=0.0, value=11.5)
        w = st.number_input("Width", min_value=0.0, value=4.0)

    if st.button("Predict Weight", type="primary"):
        # Combine inputs into a numeric array
        input_data = np.array([[l1, l2, l3, h, w]])
        
        # 1. Transform inputs to polynomial features (degree 2)
        poly_features = poly.transform(input_data)
        
        # 2. Predict weight using the regression model
        prediction = model.predict(poly_features)
        
        # Show result (Intercept is approx 256.40 in your pkl)
        st.metric(label="Predicted Weight", value=f"{max(0, prediction[0]):.2f} grams")
        st.balloons()
else:
    st.error("❌ 'Fish_model.pkl' not found in this folder.")

st.divider()
st.caption("Model scikit-learn version: 1.6.1")
