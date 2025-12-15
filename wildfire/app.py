import streamlit as st
import pickle
import numpy as np

# Set page config first
st.set_page_config(page_title="Wildfire Prediction App", layout="centered")

def main():
    st.title("🔥 Wildfire Prediction System")
    st.markdown("Predict wildfire risk based on weather indices.")

    # --- Step 1: Model Loading ---
    st.sidebar.header("Model Configuration")
    uploaded_file = st.sidebar.file_uploader("Upload your model (wildfire.pkl)", type=['pkl'])

    if uploaded_file is not None:
        try:
            model = pickle.load(uploaded_file)
            st.sidebar.success("Model loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error loading model: {e}")
            st.stop()
    else:
        st.info("⬅️ Please upload the 'wildfire.pkl' file in the sidebar to start.")
        st.stop()

    # --- Step 2: User Inputs ---
    # Create two columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Weather Data")
        temp = st.number_input("Temperature (°C)", min_value=0.0, max_value=60.0, value=30.0, step=0.1)
        rh = st.number_input("Relative Humidity (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
        ws = st.number_input("Wind Speed (km/h)", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
        rain = st.number_input("Rainfall (mm)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

    with col2:
        st.subheader("FWI Components")
        ffmc = st.number_input("Fine Fuel Moisture Code (FFMC)", min_value=0.0, max_value=100.0, value=80.0, step=0.1)
        dmc = st.number_input("Duff Moisture Code (DMC)", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
        dc = st.number_input("Drought Code (DC)", min_value=0.0, max_value=1000.0, value=50.0, step=0.1)
        isi = st.number_input("Initial Spread Index (ISI)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        bui = st.number_input("Buildup Index (BUI)", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
        fwi = st.number_input("Fire Weather Index (FWI)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

    # --- Step 3: Prediction ---
    if st.button("Predict Wildfire Risk", type="primary"):
        # Arrange features in the standard Algerian Dataset Order
        # [Temp, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI, FWI]
        features = np.array([[temp, rh, ws, rain, ffmc, dmc, dc, isi, bui, fwi]])
        
        try:
            prediction = model.predict(features)
            
            # Logic for result display
            if prediction[0] == 1 or str(prediction[0]).lower() in ['fire', '1']:
                st.error("⚠️ Prediction: High Risk of Wildfire!")
            else:
                st.success("✅ Prediction: Low Risk / No Wildfire")
                st.balloons()
                
        except Exception as e:
            st.error(f"Prediction Error: {e}")
            st.warning("Ensure your model expects 10 inputs in this order: [Temp, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI, FWI]")

if __name__ == '__main__':
    main()
