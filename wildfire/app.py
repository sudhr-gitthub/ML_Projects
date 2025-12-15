import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# --- Page Config ---
st.set_page_config(page_title="Wildfire Prediction", layout="wide")

# --- Load Model ---
@st.cache_resource
def load_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'wildfire.pkl')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

model = load_model()

# --- App Header ---
st.title("🔥 Wildfire Prediction System (Debug Mode)")

if model is None:
    st.error("❌ Model not found. Please upload 'wildfire.pkl'.")
    st.stop()

# --- DIAGNOSTICS: Check Expected Features ---
# This block checks exactly what the model wants
expected_features = getattr(model, "n_features_in_", 10)
st.info(f"🧠 **Model Diagnostics:** Your model expects **{expected_features}** input features.")

# --- Sidebar Inputs ---
st.sidebar.header("User Inputs")

def user_input_features():
    # 1. Standard 10 Features
    st.sidebar.subheader("Weather & FWI")
    temp = st.sidebar.slider('Temperature (°C)', 20.0, 50.0, 32.0)
    rh = st.sidebar.slider('Relative Humidity (%)', 10.0, 90.0, 45.0)
    ws = st.sidebar.slider('Wind Speed (km/h)', 0.0, 50.0, 14.0)
    rain = st.sidebar.slider('Rainfall (mm)', 0.0, 20.0, 0.0)
    ffmc = st.sidebar.slider('FFMC', 28.6, 92.5, 80.0)
    dmc = st.sidebar.slider('DMC', 1.1, 65.9, 20.0)
    dc = st.sidebar.slider('DC', 7.0, 220.4, 50.0)
    isi = st.sidebar.slider('ISI', 0.0, 18.5, 8.0)
    bui = st.sidebar.slider('BUI', 1.1, 68.0, 20.0)
    fwi = st.sidebar.slider('FWI', 0.0, 31.1, 10.0)

    data = {
        'Temperature': temp, 'RH': rh, 'Ws': ws, 'Rain': rain,
        'FFMC': ffmc, 'DMC': dmc, 'DC': dc, 'ISI': isi, 'BUI': bui, 'FWI': fwi
    }
    
    # 2. AUTO-FIX for 11 Features (Likely "Region")
    if expected_features == 11:
        st.sidebar.subheader("📍 Location")
        region = st.sidebar.radio("Select Region", ("Bejaia (0)", "Sidi Bel-abbes (1)"))
        region_val = 0 if "Bejaia" in region else 1
        data['Region'] = region_val
        st.success("✅ Added 'Region' feature automatically to match model.")
        
    # 3. AUTO-FIX for 12 Features (Likely Region + Date/Classes?)
    elif expected_features == 12:
        st.sidebar.subheader("📍 Extra Features")
        region = st.sidebar.radio("Region", (0, 1), index=0)
        extra_dummy = st.sidebar.number_input("Extra Feature (Dummy)", 0, 1, 0)
        data['Region'] = region
        data['Dummy'] = extra_dummy
        st.warning("⚠️ Model expects 12 features. Added Region + 1 dummy input.")

    return pd.DataFrame(data, index=[0])

input_df = user_input_features()

# --- Main Section ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Inputs Sent to Model")
    st.dataframe(input_df, hide_index=True)

    if expected_features != input_df.shape[1]:
        st.error(f"❌ CRITICAL ERROR: Model wants {expected_features} columns, but we have {input_df.shape[1]}.")
        st.stop()

    try:
        prediction = model.predict(input_df)
        
        st.markdown("---")
        st.subheader("Prediction Result")
        
        if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
            st.error("⚠️ HIGH FIRE RISK DETECTED")
        else:
            st.success("✅ LOW FIRE RISK")
            
    except Exception as e:
        st.error(f"Prediction Error: {e}")

with col2:
    st.info("ℹ️ Using Debug Mode to match model inputs.")
