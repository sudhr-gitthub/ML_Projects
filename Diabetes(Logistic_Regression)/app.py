import streamlit as st
import pandas as pd
import joblib
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Diabetes Prediction",
    page_icon="🏥",
    layout="centered"
)

# 2. Load Model Function (Robust Path Handling)
@st.cache_resource
def load_model():
    # Get the directory where THIS app.py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Join the directory with the model file name
    model_path = os.path.join(current_dir, 'Diabetes (Logistic Regression).pkl')
    
    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error(f"⚠️ Model file not found!")
        st.write(f"The app looked for the file here: `{model_path}`")
        st.info("Please make sure 'Diabetes (Logistic Regression).pkl' is in the exact same folder as 'app.py'.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the model: {e}")
        return None

# 3. Main Application
def main():
    st.title("🏥 Diabetes Prediction Tool")
    st.write("Enter patient details to predict diabetes risk.")
    
    # Load the model
    model = load_model()
    
    if model:
        st.divider()
        st.subheader("Patient Vitals")
        
        # Input Columns
        col1, col2 = st.columns(2)
        
        with col1:
            # [cite_start]Feature: age [cite: 1]
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            # [cite_start]Feature: plas (Glucose) [cite: 1]
            plas = st.number_input("Glucose Concentration (plas)", min_value=0, max_value=500, value=100)
            
        with col2:
            # [cite_start]Feature: mass (BMI) [cite: 1]
            mass = st.number_input("BMI (mass)", min_value=0.0, max_value=100.0, value=25.0, format="%.1f")
            # [cite_start]Feature: insu (Insulin) [cite: 1]
            insu = st.number_input("Serum Insulin (insu)", min_value=0, max_value=1000, value=80)

        # Prediction Button
        if st.button("Predict Status", type="primary", use_container_width=True):
            
            # [cite_start]Prepare data frame with exact feature names expected by the model [cite: 1]
            input_data = pd.DataFrame({
                'age': [age],
                'mass': [mass],
                'insu': [insu],
                'plas': [plas]
            })

            # Make Prediction
            prediction = model.predict(input_data)[0]
            
            # Display Result
            st.divider()
            st.subheader("Result:")
            
            # [cite_start]Classes are 'tested_negative' and 'tested_positive' [cite: 1]
            if prediction == 'tested_positive':
                st.error(f"**{prediction}**")
                st.warning("The model suggests a high likelihood of diabetes.")
            else:
                st.success(f"**{prediction}**")
                st.balloons()
                st.info("The model suggests a low likelihood of diabetes.")

if __name__ == "__main__":
    main()
