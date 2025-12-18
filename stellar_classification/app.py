import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os

# Page Configuration
st.set_page_config(
    page_title="Stellar Classification",
    page_icon="🌌",
    layout="centered"
)

# Title and Description
st.title("🌌 Stellar Object Classification")
st.write("Predict whether the object is a Star, Galaxy, or Quasar (QSO).")

# --- Load Model ---
@st.cache_resource
def load_model():
    try:
        # Get the absolute path to the file to avoid "File not found" errors
        model_path = os.path.join(os.path.dirname(__file__), 'stellar_classifier.pkl')
        
        # CRITICAL FIX: Use joblib.load instead of pickle.load
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- Input Form ---
if model is not None:
    st.subheader("Enter Observation Data")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Coordinates")
            alpha = st.number_input("Alpha (Right Ascension)", value=135.0, format="%.6f")
            delta = st.number_input("Delta (Declination)", value=32.0, format="%.6f")
            
            st.markdown("### Photometric Filters")
            u = st.number_input("u (Ultraviolet)", value=23.0, format="%.4f")
            g = st.number_input("g (Green)", value=22.0, format="%.4f")
            r = st.number_input("r (Red)", value=22.0, format="%.4f")

        with col2:
            st.markdown("### Filter Cont. & Others")
            i = st.number_input("i (Near Infrared)", value=19.0, format="%.4f")
            z = st.number_input("z (Infrared)", value=18.0, format="%.4f")
            
            st.markdown("### Spectroscopy")
            redshift = st.number_input("Redshift", value=0.0, format="%.6f")
            mjd = st.number_input("MJD (Modified Julian Date)", value=55000.0, format="%.1f")
            fiber_id = st.number_input("Fiber ID", value=100, step=1)

        submit_button = st.form_submit_button("Classify Object")

    # --- Prediction Logic ---
    if submit_button:
        # Create a dataframe with the exact feature names the model expects
        input_data = pd.DataFrame([[
            alpha, delta, u, g, r, i, z, redshift, mjd, fiber_id
        ]], columns=['alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'redshift', 'MJD', 'fiber_ID'])
        
        try:
            prediction = model.predict(input_data)[0]
            
            # Map the result if necessary (adjust based on your specific training labels)
            # Common SDSS mapping: 0=Galaxy, 1=QSO, 2=Star OR String outputs
            class_mapping = {0: "GALAXY", 1: "QSO", 2: "STAR"}
            
            result_text = prediction
            if isinstance(prediction, (int, np.integer)) and prediction in class_mapping:
                result_text = class_mapping[prediction]
            
            st.success(f"### Prediction: {result_text}")
            
            # Show probabilities if available
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(input_data)[0]
                classes = model.classes_
                proba_df = pd.DataFrame(proba, index=classes, columns=["Probability"])
                st.bar_chart(proba_df)

        except Exception as e:
            st.error(f"Prediction Error: {e}")
