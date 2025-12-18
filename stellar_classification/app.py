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

st.title("🌌 Stellar Object Classification")
st.write("Predict whether the object is a Star, Galaxy, or Quasar (QSO) based on Redshift.")

# --- Load Model ---
@st.cache_resource
def load_model():
    try:
        # Load using joblib
        model_path = os.path.join(os.path.dirname(__file__), 'stellar_classifier.pkl')
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- Simplified Input Form ---
if model is not None:
    with st.form("prediction_form"):
        # We only need Redshift because the model ignores everything else
        redshift = st.number_input(
            "Redshift Value", 
            value=0.0, 
            format="%.6f",
            help="The main indicator for this model. Values near 0 are usually Stars."
        )
        
        submit_button = st.form_submit_button("Classify Object")

    # --- Prediction Logic ---
    if submit_button:
        # The model still expects 10 columns, even if it doesn't use them.
        # We place 'redshift' at index 7 and fill the rest with 0.
        # Feature order: ['alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'redshift', 'MJD', 'fiber_ID']
        
        input_data = pd.DataFrame([[
            0,   # alpha (ignored)
            0,   # delta (ignored)
            0,   # u (ignored)
            0,   # g (ignored)
            0,   # r (ignored)
            0,   # i (ignored)
            0,   # z (ignored)
            redshift, # <--- The only one that matters
            0,   # MJD (ignored)
            0    # fiber_ID (ignored)
        ]], columns=['alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'redshift', 'MJD', 'fiber_ID'])
        
        try:
            prediction = model.predict(input_data)[0]
            
            # Mapping: 0=Galaxy, 1=QSO, 2=Star
            class_mapping = {0: "GALAXY", 1: "QSO", 2: "STAR"}
            
            result_text = prediction
            if isinstance(prediction, (int, np.integer)) and prediction in class_mapping:
                result_text = class_mapping[prediction]
            
            st.success(f"### Prediction: {result_text}")
            
            # Optional: Context info
            if result_text == "STAR":
                st.info("Objects with very low redshift are typically Stars in our own galaxy.")
            elif result_text == "QSO":
                st.info("Quasars (QSO) typically have high redshift values.")
            else:
                st.info("Galaxies typically have moderate redshift values.")

        except Exception as e:
            st.error(f"Prediction Error: {e}")
