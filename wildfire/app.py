import streamlit as st
import pickle
import numpy as np

# Load the trained model
# Ensure 'wildfire.pkl' is in the same directory as app.py
try:
    model = pickle.load(open('wildfire.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model file 'wildfire.pkl' not found. Please upload it to the directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

def main():
    st.set_page_config(page_title="Wildfire Prediction App", layout="centered")
    
    st.title("🔥 Wildfire Prediction System")
    st.markdown("Enter the weather indices below to predict the occurrence of a wildfire.")

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

    # Prediction button
    if st.button("Predict Wildfire Risk"):
        # Arrange features in the order the model expects
        # Standard Algerian Dataset Order: [Temp, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI, FWI]
        features = np.array([[temp, rh, ws, rain, ffmc, dmc, dc, isi, bui, fwi]])
        
        try:
            prediction = model.predict(features)
            
            # Assuming the model returns 1 for Fire and 0 for No Fire (or similar classes)
            if prediction[0] == 1 or prediction[0] == 'fire':
                st.error("⚠️ Prediction: High Risk of Wildfire!")
                st.image("https://media.giphy.com/media/3o6ozh46EbuWRYAcSY/giphy.gif", caption="Danger Alert", width=300)
            else:
                st.success("✅ Prediction: Low Risk / No Wildfire")
                st.balloons()
                
        except ValueError as e:
            st.error(f"Error during prediction. The model might expect a different number of features.\nDetails: {e}")

if __name__ == '__main__':
    main()
