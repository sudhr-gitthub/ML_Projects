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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'wildfire.pkl')
    
    if not os.path.exists(model_path):
        st.error("❌ Error: 'wildfire.pkl' not found.")
        st.warning(f"Please run 'python create_model.py' to generate the model file first.")
        return None

    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None

model = load_model()

# --- Sidebar Inputs ---
st.sidebar.header("User Input Parameters")

def user_input_features():
    st.sidebar.subheader("🌤️ Weather Data")
    temp = st.sidebar.slider('Temperature (°C)', 20.0, 42.0, 32.0)
    rh = st.sidebar.slider('Relative Humidity (%)', 21.0, 90.0, 45.0)
    ws = st.sidebar.slider('Wind Speed (km/h)', 6.0, 29.0, 14.0)
    rain = st.sidebar.slider('Rainfall (mm)', 0.0, 16.8, 0.0)

    st.sidebar.subheader("🌲 FWI Indices")
    ffmc = st.sidebar.slider('Fine Fuel Moisture Code (FFMC)', 28.6, 92.5, 80.0)
    dmc = st.sidebar.slider('Duff Moisture Code (DMC)', 1.1, 65.9, 20.0)
    dc = st.sidebar.slider('Drought Code (DC)', 7.0, 220.4, 50.0)
    isi = st.sidebar.slider('Initial Spread Index (ISI)', 0.0, 18.5, 8.0)
    bui = st.sidebar.slider('Buildup Index (BUI)', 1.1, 68.0, 20.0)
    fwi = st.sidebar.slider('Fire Weather Index (FWI)', 0.0, 31.1, 10.0)

    data = {
        'Temperature': temp, 'RH': rh, 'Ws': ws, 'Rain': rain,
        'FFMC': ffmc, 'DMC': dmc, 'DC': dc, 'ISI': isi, 'BUI': bui, 'FWI': fwi
    }
    return pd.DataFrame(data, index=[0])

input_df = user_input_features()

# --- Main Layout ---
st.title("🔥 Wildfire Prediction System")
st.markdown("Adjust the sidebar sliders to see the prediction update in real-time.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Parameters")
    st.dataframe(input_df, hide_index=True)
    st.markdown("---")
    
    # --- AUTOMATIC PREDICTION ---
    if model is not None:
        try:
            # Check feature count mismatch before predicting
            if hasattr(model, "n_features_in_") and model.n_features_in_ != input_df.shape[1]:
                st.error(f"⚠️ Model Mismatch: Model expects {model.n_features_in_} features, but app provides {input_df.shape[1]}.")
                st.info("Run 'python create_model.py' to fix this.")
            else:
                prediction = model.predict(input_df)
                
                # Try to get probability
                try:
                    proba = model.predict_proba(input_df)[0][1] * 100
                    proba_text = f"Confidence: {proba:.2f}%"
                except:
                    proba_text = ""

                st.subheader("Prediction Result")
                if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
                    st.error("⚠️ DANGER: HIGH FIRE RISK")
                    st.write(f"The model predicts a high risk of fire. {proba_text}")
                else:
                    st.success("✅ SAFE: LOW FIRE RISK")
                    st.write(f"The conditions are safe. {proba_text}")

        except Exception as e:
            st.error(f"Prediction Error: {e}")
    else:
        st.warning("Model not loaded.")

with col2:
    st.info("ℹ️ **About the Indices**")
    st.markdown("""
    **FWI System Components:**
    * **FFMC:** Fine Fuel Moisture Code
    * **DMC:** Duff Moisture Code
    * **DC:** Drought Code
    * **ISI:** Initial Spread Index
    * **BUI:** Buildup Index
    * **FWI:** Fire Weather Index
    """)
