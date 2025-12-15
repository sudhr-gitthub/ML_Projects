import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Stellar Classification",
    page_icon="🌌",
    layout="centered"
)

# Title and Description
st.title("🌌 Stellar Classification App")
st.write("This app uses a Machine Learning model to classify astronomical objects into Stars, Galaxies, or Quasars based on spectral data.")

# --- Load Model ---
@st.cache_resource
def load_model():
    try:
        # Load the model file
        model = joblib.load('stellar_classifier.pkl')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- Input Form ---
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

    # Submit Button
    submit_button = st.form_submit_button("Classify Object")

# --- Prediction Logic ---
if submit_button and model is not None:
    # 1. Prepare input data in the exact order the model expects
    # The order matches 'feature_names_in_' from your pkl file:
    # ['alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'redshift', 'MJD', 'fiber_ID']
    
    input_data = pd.DataFrame([[
        alpha, delta, u, g, r, i, z, redshift, mjd, fiber_id
    ]], columns=['alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'redshift', 'MJD', 'fiber_ID'])
    
    # 2. Make Prediction
    try:
        prediction = model.predict(input_data)[0]
        
        # 3. Map Prediction to Class Name
        # Standard SDSS mapping usually involves 3 classes. 
        # Adjust this dictionary if your specific training labels were different.
        class_mapping = {
            0: "GALAXY",
            1: "QSO (Quasar)",
            2: "STAR"
        }
        
        # If the model outputs strings directly, we use them; otherwise we map integers
        result = prediction
        if isinstance(prediction, (int, np.integer)) and prediction in class_mapping:
            result = class_mapping[prediction]
            
        # 4. Display Result
        st.success(f"Prediction: **{result}**")
        
        # Optional: Display probabilities if the model supports it
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)[0]
            st.write("Confidence Scores:")
            st.bar_chart(pd.DataFrame(proba, index=list(class_mapping.values()) if isinstance(prediction, (int, np.integer)) else model.classes_, columns=["Probability"]))

    except Exception as e:
        st.error(f"Error making prediction: {e}")
