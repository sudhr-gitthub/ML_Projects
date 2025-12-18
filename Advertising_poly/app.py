import streamlit as st
import pickle
import numpy as np

# Page Configuration
st.set_page_config(page_title="Advertising Sales Predictor", layout="centered")

def load_model():
    """
    Loads the model and polynomial transformer from the pickle file.
    The file contains a tuple: (LinearRegression, PolynomialFeatures)
    """
    try:
        with open('advertising_poly_model.pkl', 'rb') as file:
            data = pickle.load(file)
        return data[0], data[1] # Unpacking model and poly_converter
    except FileNotFoundError:
        st.error("File 'advertising_poly_model.pkl' not found. Please upload it to the same directory.")
        return None, None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None

def main():
    st.title("📈 Advertising Sales Predictor")
    st.write("Enter your advertising budgets below to predict sales volume.")

    # Load resources
    model, poly = load_model()

    if model and poly:
        st.write("---")
        
        # Input Form
        with st.form("prediction_form"):
            st.header("Advertising Budget parameters")
            
            # The model was trained on: ['TV', 'Radio', 'Newspaper']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tv_budget = st.number_input("TV Budget ($)", min_value=0.0, value=100.0, step=10.0)
            
            with col2:
                radio_budget = st.number_input("Radio Budget ($)", min_value=0.0, value=25.0, step=1.0)
                
            with col3:
                news_budget = st.number_input("Newspaper Budget ($)", min_value=0.0, value=10.0, step=1.0)
            
            submit_btn = st.form_submit_button("Predict Sales")

        # Prediction Logic
        if submit_btn:
            # 1. Prepare input array
            input_data = np.array([[tv_budget, radio_budget, news_budget]])
            
            # 2. Transform input using the loaded PolynomialFeatures
            # This expands the 3 inputs into 9 features (degree 2 interaction terms)
            input_transformed = poly.transform(input_data)
            
            # 3. Predict using the LinearRegression model
            prediction = model.predict(input_transformed)
            
            # 4. Display Result
            st.success(f"### Predicted Sales: {prediction[0]:.2f}")
            st.info(f"Model used: Polynomial Regression (Degree {poly.degree})")

if __name__ == "__main__":
    main()
