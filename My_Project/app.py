import streamlit as st
import pickle
import numpy as np

# Page configuration
st.set_page_config(page_title="Salary Prediction App", layout="centered")

# Title
st.title("💼 Salary Prediction using Linear Regression")
st.write("Enter years of experience to predict salary")

# Load trained model
with open("Salary_Prediction_model.pkl", "rb") as file:
    model = pickle.load(file)

# User input
experience = st.number_input(
    "Years of Experience",
    min_value=0.0,
    max_value=50.0,
    step=0.1
)

# Prediction button
if st.button("Predict Salary"):
    exp_array = np.array([[experience]])
    prediction = model.predict(exp_array)

    st.success(f"💰 Predicted Salary: ₹ {prediction[0]:,.2f}")

