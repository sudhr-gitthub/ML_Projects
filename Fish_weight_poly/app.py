import streamlit as st
import numpy as np
import pickle
import os

# 1. Page Configuration
st.set_page_config(page_title="Fish Weight Predictor", page_icon="🐟")

st.title("🐟 Fish Weight Prediction")
st.write("Enter the fish dimensions to predict its weight.")

# 2. Model Loading Logic
@st.cache_resource
def load_model():
    # Looking for the file in the same folder as this script
    model_name = "Fish_model.pkl"
    
    if os.path.exists(model_name):
        try:
            with open(model_name, "rb") as f:
                # The file contains: (PolynomialFeatures, LinearRegression)
                data = pickle.load(f)
                return data[0], data[1] # poly_transformer, regressor
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None, None
    else:
        return None, None

# Try to load the model
poly, model = load_model()

# 3. User Interface
if poly is not None and model is not None:
    st.success("✅ Model loaded successfully!")
    
    st.subheader("Input Measurements (Numbers Only)")
    
    # Using columns for a clean layout
    col1, col2 = st.columns(2)
    
    with col1:
        # st.number_input ensures only numbers can be entered
        l1 = st.number_input("Vertical Length (Length1) in cm", min_value=0.0, value=23.2, step=0.1)
        l2 = st.number_input("Diagonal Length (Length2) in cm", min_value=0.0, value=25.4, step=0.1)
        l3 = st.number_input("Cross Length (Length3) in cm", min_value=0.0, value=30.0, step=0.1)
    
    with col2:
        h = st.number_input("Height in cm", min_value=0.0, value=11.5, step=0.1)
        w = st.number_input("Width in cm", min_value=0.0, value=4.0, step=0.1)

    # 4. Prediction Button
    if st.button("Predict Weight", type="primary"):
        # Convert inputs to a numpy array
        features = np.array([[l1, l2, l3, h, w]])
        
        # Step A: Transform inputs into Polynomial features
        poly_features = poly.transform(features)
        
        # Step B: Predict using the Linear Regression model
        prediction = model.predict(poly_features)
        
        # Show result
        st.metric(label="Predicted Fish Weight", value=f"{max(0, prediction[0]):.2f} grams")
        st.balloons()

else:
    # ERROR HANDLING AND DEBUGGING
    st.error("❌ 'Fish_model.pkl' was not found in the current folder.")
    
    st.info("📂 **Debug Info for you:**")
    st.write(f"Your app is running in: `{os.getcwd()}`")
    st.write("Files found in this folder:", os.listdir("."))
    
    st.markdown("""
    ### How to fix this:
    1. Make sure your model file is named exactly **`Fish_model.pkl`**.
    2. Ensure the model file is in the **same folder** as this `app.py`.
    3. If using **GitHub/Streamlit Cloud**, upload the `.pkl` file to your repository.
    """)

st.divider()
st.caption("Model Version: scikit-learn 1.6.1 | Features: Length1, Length2, Length3, Height, Width")
