import streamlit as st
import joblib
import numpy as np
import os

# Set page configuration
st.set_page_config(page_title="Iris Species Predictor", page_icon="🌸")

# Cached function to load the model (prevents reloading on every interaction)
@st.cache_resource
def load_model():
    model_path = 'svm_iris_model.pkl'
    if not os.path.exists(model_path):
        st.error(f"Model file not found: {model_path}. Please ensure it is in the same directory.")
        return None
    return joblib.load(model_path)

def main():
    st.title("🌸 Iris Flower Classifier")
    st.write("Enter the flower measurements below to predict the species.")

    # Load the model
    model = load_model()

    if model:
        # Create a form for input
        with st.form("prediction_form"):
            st.header("Input Features")
            
            # Grouping inputs into columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Features based on 
                sepal_length = st.number_input("Sepal Length (cm)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
                sepal_width = st.number_input("Sepal Width (cm)", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
            
            with col2:
                petal_length = st.number_input("Petal Length (cm)", min_value=0.0, max_value=10.0, value=1.4, step=0.1)
                petal_width = st.number_input("Petal Width (cm)", min_value=0.0, max_value=10.0, value=0.2, step=0.1)
            
            # Submit button
            submitted = st.form_submit_button("Predict Species")

        # logic to handle prediction
        if submitted:
            # Reshape input to 2D array as required by sklearn
            features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
            
            try:
                prediction = model.predict(features)
                species = prediction[0] # 
                
                st.success(f"The predicted species is: **{species}**")
                
                # Optional: Add an image or extra details based on the class
                if species == 'setosa':
                    st.info("Setosa irises are typically small and grow in wetlands.")
                elif species == 'versicolor':
                    st.info("Versicolor is a common iris species found in North America.")
                elif species == 'virginica':
                    st.info("Virginica irises are known for their taller stems.")
                    
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

if __name__ == '__main__':
    main()
