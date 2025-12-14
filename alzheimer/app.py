# ML_Projects/alzheimer/app.py

import streamlit as st
import joblib
import numpy as np
import pandas as pd
# Import the module for robust path handling
from pathlib import Path

# The file name of the model
MODEL_FILE_NAME = 'alzheimers_logreg.pkl'

# Use st.cache_resource to load the model only once, improving performance.
# This assumes the model file is located in the same directory as this app.py.
@st.cache_resource
def load_model():
    """Loads the machine learning model using an absolute path to ensure success."""
    
    # 1. Get the directory of the current script (app.py)
    # This finds the directory: /path/to/ML_Projects/alzheimer/
    BASE_DIR = Path(__file__).resolve().parent
    
    # 2. Construct the full path to the model file
    # This results in: /path/to/ML_Projects/alzheimer/alzheimers_logreg.pkl
    model_path = BASE_DIR / MODEL_FILE_NAME
    
    # Convert to string for joblib.load
    file_path = str(model_path)
    
    try:
        st.info(f"Attempting to load model from path: {file_path}")
        model = joblib.load(file_path)
        st.success(f"Model '{MODEL_FILE_NAME}' loaded successfully!")
        return model
    except FileNotFoundError:
        st.error(f"FATAL ERROR: Model file not found at the computed path: {file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        st.stop()

# --- Load Model and Set up App ---

st.title("Alzheimer's Prediction App")
st.markdown("---")

# Load the model (Notice: we don't pass the name anymore, the function figures it out)
model = load_model()

# ... (The rest of your code for input fields and prediction goes here)
# ... (It does not need to change)
# ...
