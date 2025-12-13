import streamlit as st
import pickle
import numpy as np
import os  # <--- Add this import

st.set_page_config(page_title="Salary Prediction", layout="centered")

st.title("💼 Salary Prediction using Linear Regression")
st.write("Enter years of experience to predict salary")

# Get the absolute path to the current directory
current_dir = os.path.dirname(__file__)

# Join the directory with the model filename
model_path = os.path.join(current_dir, "salary_model.pkl")

# Load model using the absolute path
with open(model_path, "rb") as file:
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
