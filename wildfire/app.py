import streamlit as st
import pickle
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(page_title="Wildfire Prediction", page_icon="🔥", layout="centered")

def main():
    # --- 1. Display Banner Image ---
    st.image(
        "https://images.unsplash.com/photo-1590418606746-018840f9cd0f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80", 
        caption="Forest Fire Risk Assessment System",
        use_column_width=True
    )

    st.title("🔥 Wildfire Prediction System")
    st.markdown("Enter the weather conditions below to assess the risk of a forest fire.")
    st.markdown("---")

    # --- 2. Robust Model Loading ---
    # This block gets the absolute path of the current file (app.py)
    # and forces Python to look for 'wildfire.pkl' in the EXACT same folder.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'wildfire.pkl')

    if not os.path.exists(model_path):
        st.error(f"❌ Error: Model file not found.")
        st.error(f"Looking for: **{model_path}**")
        st.warning("👉 Solution: Move your 'wildfire.pkl' file into this specific folder shown above.")
        st.stop()

    try:
        model = pickle.load(open(model_path, 'rb'))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

    # --- 3. User Inputs ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌡️ Weather Data")
        temp = st.number_input("Temperature (°C)", 20.0, 50.0, 30.0)
        rh = st.number_input("Relative Humidity (%)", 10.0, 90.0, 50.0)
        ws = st.number_input("Wind Speed (km/h)", 0.0, 50.0, 15.0)
        rain = st.number_input("Rainfall (mm)", 0.0, 20.0, 0.0)

    with col2:
        st.subheader("🌲 FWI Components")
        ffmc = st.number_input("FFMC Index", 0.0, 100.0, 80.0)
        dmc = st.number_input("DMC Index", 0.0, 100.0, 15.0)
        dc = st.number_input("DC Index", 0.0, 200.0, 50.0)
        isi = st.number_input("ISI Index", 0.0, 50.0, 5.0)
        bui = st.number_input("BUI Index", 0.0, 100.0, 15.0)
        fwi = st.number_input("FWI Index", 0.0, 100.0, 5.0)

    st.markdown("---")

    # --- 4. Prediction Logic ---
    if st.button("Analyze Risk", type="primary", use_container_width=True):
        # The model expects a 2D array of features
        features = np.array([[temp, rh, ws, rain, ffmc, dmc, dc, isi, bui, fwi]])
        
        try:
            prediction = model.predict(features)
            
            result_container = st.container()
            
            # Check result (1/fire = High Risk, 0/not fire = Low Risk)
            if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
                with result_container:
                    st.error("⚠️ DANGER: HIGH WILDFIRE RISK DETECTED")
                    st.markdown("### Status: **Fire Likely**")
                    st.image("https://media.giphy.com/media/l0IXYpBrw6gD6XzFK/giphy.gif", width=300)
            else:
                with result_container:
                    st.success("✅ SAFE: LOW WILDFIRE RISK")
                    st.markdown("### Status: **No Fire**")
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Prediction Error: {e}")

if __name__ == '__main__':
    main()
