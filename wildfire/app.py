import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# --- Page Config ---
st.set_page_config(
    page_title="Wildfire Prediction",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Robust Model Loading ---
@st.cache_resource
def load_model():
    """
    Loads the model using joblib.
    Uses absolute paths to prevent 'FileNotFoundError'.
    """
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'wildfire.pkl')
    
    if not os.path.exists(model_path):
        st.error(f"❌ Critical Error: Model file not found.")
        st.warning(f"Please place 'wildfire.pkl' in this folder: {current_dir}")
        return None

    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        st.info("Ensure the file isn't corrupted and was uploaded correctly to GitHub.")
        return None

# Load the model
model = load_model()

# --- Main Page Header ---
st.title("🔥 Wildfire Prediction System")
st.markdown("""
This application uses Machine Learning to predict the likelihood of a forest fire based on weather indices.
**Adjust the parameters in the sidebar** to see the prediction update.
""")

# --- Sidebar Inputs ---
st.sidebar.header("User Input Parameters")

def user_input_features():
    # Weather Data
    st.sidebar.subheader("🌤️ Weather Data")
    temp = st.sidebar.slider('Temperature (°C)', 20.0, 42.0, 32.0)
    rh = st.sidebar.slider('Relative Humidity (%)', 21.0, 90.0, 45.0)
    ws = st.sidebar.slider('Wind Speed (km/h)', 6.0, 29.0, 14.0)
    rain = st.sidebar.slider('Rainfall (mm)', 0.0, 16.8, 0.0)

    # FWI Components
    st.sidebar.subheader("🌲 FWI Indices")
    ffmc = st.sidebar.slider('Fine Fuel Moisture Code (FFMC)', 28.6, 92.5, 80.0)
    dmc = st.sidebar.slider('Duff Moisture Code (DMC)', 1.1, 65.9, 20.0)
    dc = st.sidebar.slider('Drought Code (DC)', 7.0, 220.4, 50.0)
    isi = st.sidebar.slider('Initial Spread Index (ISI)', 0.0, 18.5, 8.0)
    bui = st.sidebar.slider('Buildup Index (BUI)', 1.1, 68.0, 20.0)
    fwi = st.sidebar.slider('Fire Weather Index (FWI)', 0.0, 31.1, 10.0)

    # Store in DataFrame (matches model training format)
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
    return pd.DataFrame(data, index=[0])

# Get inputs
input_df = user_input_features()

# --- Main Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Parameters")
    st.write(input_df)

    if st.button('Predict Fire Risk', type="primary", use_container_width=True):
        if model is not None:
            # Predict
            prediction = model.predict(input_df)
            
            # Use try-except for probability in case model doesn't support it
            try:
                probability = model.predict_proba(input_df)[0][1]
                prob_msg = f"Probability: {probability*100:.2f}%"
            except:
                prob_msg = ""

            st.markdown("---")
            st.subheader("Prediction Result")

            # Logic: 1 = Fire, 0 = No Fire
            if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
                st.error("⚠️ DANGER: HIGH FIRE RISK")
                st.write("The model predicts a high likelihood of forest fire.")
                if prob_msg: st.write(f"**{prob_msg}**")
            else:
                st.success("✅ SAFE: LOW FIRE RISK")
                st.write("The model predicts conditions are safe.")
                if prob_msg: st.write(f"**{prob_msg}**")
        else:
            st.error("Model is not loaded. Please check the sidebar for errors.")

with col2:
    # Information Section
    st.info("ℹ️ **About the Indices**")
    st.markdown("""
    * **FFMC:** Fine Fuel Moisture Code
    * **DMC:** Duff Moisture Code
    * **DC:** Drought Code
    * **ISI:** Initial Spread Index
    * **BUI:** Buildup Index
    * **FWI:** Fire Weather Index
    """)
