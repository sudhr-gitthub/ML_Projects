import streamlit as st
import pandas as pd
import joblib
import os

# Set page configuration
st.set_page_config(page_title="Diabetes Prediction App", layout="centered")

@st.cache_resource
def load_model():
    # Check if file exists to avoid crashing if missing
    model_path = 'Diabetes (Logistic Regression).pkl'
    if not os.path.exists(model_path):
        st.error(f"Model file '{model_path}' not found. Please ensure it is in the same directory as app.py.")
        return None
    return joblib.load(model_path)

def main():
    st.title("🏥 Diabetes Prediction Tool")
    st.write("Enter the patient details below to predict the likelihood of diabetes.")

    # Load the model
    model = load_model()

    if model:
        # Create input fields matching the model's feature names: ['age', 'mass', 'insu', 'plas']
        st.subheader("Patient Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)
            plas = st.number_input("Glucose Concentration (plas)", min_value=0, max_value=300, value=100)
            
        with col2:
            mass = st.number_input("Body Mass Index (mass)", min_value=0.0, max_value=70.0, value=25.0)
            insu = st.number_input("Serum Insulin (insu)", min_value=0, max_value=900, value=80)

        # Create a button for prediction
        if st.button("Predict Result", type="primary"):
            # Prepare the input data as a DataFrame (required for feature name matching)
            input_data = pd.DataFrame({
                'age': [age],
                'mass': [mass],
                'insu': [insu],
                'plas': [plas]
            })

            # Make prediction
            try:
                prediction = model.predict(input_data)[0]
                
                # Display result
                st.markdown("---")
                if prediction == 'tested_positive':
                    st.error(f"**Prediction:** {prediction}")
                    st.warning("The model predicts the patient **has diabetes**.")
                else:
                    st.success(f"**Prediction:** {prediction}")
                    st.info("The model predicts the patient is **negative for diabetes**.")
                    
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

if __name__ == "__main__":
    main()
