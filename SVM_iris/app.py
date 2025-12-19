import streamlit as st
import joblib
import numpy as np
import os

# Set page configuration
st.set_page_config(page_title="Iris Species Predictor", page_icon="🌸")

@st.cache_resource
def load_model():
    # ---------------------------------------------------------
    # MAGIC FIX: Get the absolute path of the directory where this script is located
    # ---------------------------------------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the model file
    model_path = os.path.join(script_dir, 'svm_iris_model.pkl')
    
    # Check if file exists at that exact path
    if not os.path.exists(model_path):
        st.error(f"❌ Model file not found at: {model_path}")
        st.warning("Please make sure 'svm_iris_model.pkl' is in the exact same folder as 'app.py'.")
        return None
        
    try:
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"❌ Error loading the model: {e}")
        return None

def main():
    st.title("🌸 Iris Flower Classifier")
    st.write("Enter the flower measurements below to predict the species.")

    # Load the model
    model = load_model()

    if model:
        # Create a form for input
        with st.form("prediction_form"):
            st.header("Input Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                sepal_length = st.number_input("Sepal Length (cm)", 0.0, 10.0, 5.0, 0.1)
                sepal_width = st.number_input("Sepal Width (cm)", 0.0, 10.0, 3.5, 0.1)
            
            with col2:
                petal_length = st.number_input("Petal Length (cm)", 0.0, 10.0, 1.4, 0.1)
                petal_width = st.number_input("Petal Width (cm)", 0.0, 10.0, 0.2, 0.1)
            
            submitted = st.form_submit_button("Predict Species")

        if submitted:
            # Reshape input for the model
            features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
            
            try:
                prediction = model.predict(features)
                species = prediction[0]
                
                # Display Result
                st.success(f"The predicted species is: **{species}**")
                
                # Contextual info
                if species == 'setosa':
                    st.info("ℹ️ Setosa is easily identified by its small petals.")
                elif species == 'versicolor':
                    st.info("ℹ️ Versicolor is a versatile species found in many environments.")
                elif species == 'virginica':
                    st.info("ℹ️ Virginica is the largest of the three standard iris species.")
                    
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

if __name__ == '__main__':
    main()
