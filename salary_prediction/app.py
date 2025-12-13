import streamlit as st
import pickle
import numpy as np

st.set_page_config(page_title="Salary Prediction", layout="centered")

st.title("💼 Salary Prediction using Linear Regression")
st.write("Enter years of experience to predict salary")

# Load model
with open("salary_model.pkl", "rb") as file:
    model = pickle.load(file)

experience = st.number_input(
    "Years of Experience",
    min_value=0.0,
    max_value=50.0,
    step=0.1
)

if st.button("Predict Salary"):
    prediction = model.predict([[experience]])
    st.success(f"💰 Predicted Salary: ₹ {prediction[0]:,.2f}")
