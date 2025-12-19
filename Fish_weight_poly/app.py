import streamlit as st
import numpy as np
import pickle

st.set_page_config(page_title="Fish Weight Prediction", layout="centered")

st.title("🐟 Fish Weight Prediction")
st.write("Predict fish weight using a **Polynomial Regression model**")

# Load trained model components
# The PKL contains [PolynomialFeatures, LinearRegression]
with open("Fish_model.pkl", "rb") as f:
    # Source 1 & 2 indicate the file contains these two components sequentially
    poly, model = pickle.load(f)

st.success("✅ Model and Transformer loaded successfully")

st.subheader("Enter Fish Measurements")

# Feature names identified from the model: Length1, Length2, Length3, Height, Width
l1 = st.number_input("Vertical Length (Length1) (cm)", 0.0, 100.0, 23.2)
l2 = st.number_input("Diagonal Length (Length2) (cm)", 0.0, 100.0, 25.4)
l3 = st.number_input("Cross Length (Length3) (cm)", 0.0, 100.0, 30.0)
h  = st.number_input("Height (cm)", 0.0, 50.0, 11.5)
w  = st.number_input("Width (cm)", 0.0, 30.0, 4.0)

if st.button("Predict Weight"):
    # Create input array
    input_data = np.array([[l1, l2, l3, h, w]])
    
    # 1. Transform the input using the loaded PolynomialFeatures 
    input_poly = poly.transform(input_data)
    
    # 2. Predict using the loaded LinearRegression model [cite: 2]
    prediction = model.predict(input_poly)
    
    # Display result
    st.metric(label="Predicted Weight", value=f"{prediction[0]:.2f} grams")
    st.balloons()
