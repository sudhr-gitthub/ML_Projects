import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# Page Configuration
st.set_page_config(
    page_title="Wildfire Prediction",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Model ---
def load_model():
    # Helper to load model correctly whether locally or deployed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'wildfire.pkl')
    
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return None
    else:
        st.error("Model file 'wildfire.pkl' not found.")
        return None

model = load_model()

# --- App Layout ---
st.title("🔥 Wildfire Prediction App")
st.markdown("""
This application predicts the **Fire Weather Index (FWI)** class based on environmental parameters.
Adjust the values in the sidebar to see the prediction.
""")

# --- Sidebar Inputs ---
st.sidebar.header("User Input Parameters")

def user_input_features():
    # Weather Components
    st.sidebar.subheader("Weather Data")
    temp = st.sidebar.slider('Temperature (°C)', 20.0, 42.0, 32.0)
    rh = st.sidebar.slider('Relative Humidity (%)', 21.0, 90.0, 45.0)
    ws = st.sidebar.slider('Wind Speed (km/h)', 6.0, 29.0, 14.0)
    rain = st.sidebar.slider('Rainfall (mm)', 0.0, 16.8, 0.0)

    # FWI Components
    st.sidebar.subheader("FWI Components")
    ffmc = st.sidebar.slider('Fine Fuel Moisture Code (FFMC)', 28.6, 92.5, 80.0)
    dmc = st.sidebar.slider('Duff Moisture Code (DMC)', 1.1, 65.9, 20.0)
    dc = st.sidebar.slider('Drought Code (DC)', 7.0, 220.4, 50.0)
    isi = st.sidebar.slider('Initial Spread Index (ISI)', 0.0, 18.5, 8.0)
    bui = st.sidebar.slider('Buildup Index (BUI)', 1.1, 68.0, 20.0)
    fwi = st.sidebar.slider('Fire Weather Index (FWI)', 0.0, 31.1, 10.0)

    # Dictionary of features
    data = {
        'Temperature': temp,
        'RH': rh,
        'Ws': ws,
        'Rain': rain,
        'FFMC': ffmc,
        'DMC': dmc,
        'DC': dc,
        'ISI': isi,
        'BUI': bui,
        'FWI': fwi
    }
    features = pd.DataFrame(data, index=[0])
    return features

# Get input from sidebar
input_df = user_input_features()

# --- Main Section Display ---
st.subheader('Current Input Parameters')
st.write(input_df)

# --- Prediction ---
if st.button('Predict Fire Risk', type="primary"):
    if model is not None:
        try:
            # Convert DataFrame to numpy array for the model
            prediction = model.predict(input_df.values)
            prediction_proba = model.predict_proba(input_df.values)

            st.subheader('Prediction Result')
            
            # Handling the output (assuming 1 = Fire, 0 = No Fire)
            if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
                st.error("⚠️ PREDICTION: FIRE")
                st.write(f"Confidence: {prediction_proba[0][1] * 100:.2f}%")
            else:
                st.success("✅ PREDICTION: NO FIRE")
                st.write(f"Confidence: {prediction_proba[0][0] * 100:.2f}%")

        except Exception as e:
            st.error(f"Error making prediction: {e}")
            st.info("Ensure the input features match the model's training data exactly.")
    else:
        st.warning("Model not loaded. Please upload 'wildfire.pkl' to the app directory.")
