# app.py

import streamlit as st
import joblib
import numpy as np
import pandas as pd # Included for common ML workflow compatibility
import os

# Define the file name for the model
MODEL_FILE_NAME = 'alzheimers_logreg.pkl'

# Use st.cache_resource to load the model only once, improving performance.
# It assumes the file is in the same directory as this app.py in your GitHub repo.
@st.cache_resource
def load_model(file_path):
    """Loads the machine learning model from the local file."""
    try:
        model = joblib.load(file_path)
        st.success(f"Model '{MODEL_FILE_NAME}' loaded successfully!")
        return model
    except FileNotFoundError:
        st.error(f"Error: Model file '{file_path}' not found in the repository.")
        st.stop() # Stop the app if the crucial file is missing
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        st.stop()

# --- Load Model and Set up App ---

st.title("Alzheimer's Prediction App")
st.markdown("---")

# Load the model
model = load_model(MODEL_FILE_NAME)

st.header("Input Features for Prediction")

# --- Example Input Fields (Adapt these to your model's actual features) ---
# NOTE: The features and their order must exactly match what the model was trained on.

col1, col2, col3 = st.columns(3)
with col1:
    feature_age = st.slider("1. Age (in years)", 50, 90, 75)
with col2:
    feature_gender = st.selectbox("2. Gender", ['Male', 'Female'])
with col3:
    feature_mmse = st.number_input("3. MMSE Score (0-30)", 0.0, 30.0, 25.0)

# Preprocessing: Map categorical inputs to numerical values
gender_val = 1 if feature_gender == 'Male' else 0

# Create the input array (must be 2D for scikit-learn models)
input_data = np.array([[feature_age, gender_val, feature_mmse]])

# --- Prediction Logic ---
if st.button("Generate Prediction"):
    try:
        # Predict the class
        prediction = model.predict(input_data)
        
        # Get probability (for classification models)
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(input_data)[0]
        else:
            probabilities = None

        # Display Result
        st.subheader("Prediction Result:")
        
        if prediction[0] == 1: # Assuming '1' means High Risk/Positive
            st.error("Diagnosis: **High Risk of Alzheimer's**")
        else: # Assuming '0' means Low Risk/Negative
            st.success("Diagnosis: **Low Risk**")
            
        if probabilities is not None:
            # Assuming probabilities[0] is Low Risk and probabilities[1] is High Risk
            st.info(f"Low Risk Probability: **{probabilities[0]*100:.2f}%**")
            st.info(f"High Risk Probability: **{probabilities[1]*100:.2f}%**")

    except ValueError as ve:
        st.error(f"Prediction Error: Input shape mismatch. Check your feature count and types. Error: {ve}")
    except Exception as e:
        st.error(f"An unexpected error occurred during prediction: {e}")

# --- Deployment Context for GitHub Connection ---
st.sidebar.title("Streamlit & GitHub Connection")
st.sidebar.markdown(
    """
    To "connect" this Streamlit app to GitHub for deployment (e.g., on 
    Streamlit Community Cloud or another cloud service):

    ### 🚀 Deployment Steps:
    1. **Create GitHub Repo:** Create a new public repository (e.g., `streamlit-alzheimers-app`).
    2. **Add Files:** Upload `app.py`, `requirements.txt`, and your model file (`alzheimers_logreg.pkl`) to the root of the repository.
    3. **Deploy on Streamlit Cloud:**
       - Go to **[share.streamlit.io](https://share.streamlit.io)** and log in.
       - Click **`New App`**.
       - Select your GitHub repository and the main branch.
       - Ensure the "Main file path" is set to `app.py`.
       - Click **`Deploy!`**.
    """
)
