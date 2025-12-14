# ML_Projects/alzheimer/app.py

import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os

# Define the file name for the model
MODEL_FILE_NAME = 'alzheimers_logreg.pkl'

# Use st.cache_resource to load the model only once, improving performance.
# This assumes the model file is located in the same directory as this app.py.
@st.cache_resource
def load_model(file_path):
    """Loads the machine learning model from the local file."""
    try:
        model = joblib.load(file_path)
        st.success(f"Model '{MODEL_FILE_NAME}' loaded successfully!")
        return model
    except FileNotFoundError:
        st.error(f"Error: Model file '{file_path}' not found in the 'alzheimer/' directory.")
        st.stop()
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
# This feature vector order must match your model training data.
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
st.sidebar.title("Streamlit & GitHub Deployment")
st.sidebar.markdown(
    """
    ### 🚀 Deployment Configuration (for Streamlit Cloud):
    
    Based on your path:
    `sudhr-gitthub/ML_Projects/main/alzheimer/app.py`

    When deploying on Streamlit Community Cloud:
    
    1. **Repository:** `sudhr-gitthub/ML_Projects`
    2. **Branch:** `main`
    3. **Main file path:** `alzheimer/app.py` (Crucial change!)
    4. **Model Location:** Ensure `alzheimers_logreg.pkl` is inside the `alzheimer/` folder with `app.py`.
    5. **Dependencies:** Ensure `requirements.txt` is in the repository root (`ML_Projects/`).
    """
)
