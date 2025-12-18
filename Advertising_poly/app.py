# app.py
import streamlit as st
import pickle
import numpy as np

st.set_page_config(page_title="Advertising Sales Predictor", layout="centered")

st.title("📊 Advertising Sales Prediction")
st.write(
    "Enter your advertising budget for TV, Radio, and Newspaper to predict sales."
)

# 1️⃣ Load the trained model
@st.cache_data
def load_model():
    with open("advertising_poly_model.pkl", "rb") as f:
        model, poly = pickle.load(f)
    return model, poly

model, poly = load_model()

# 2️⃣ User input
tv = st.number_input("TV Advertising Spend ($)", min_value=0.0, value=500.0, step=10.0)
radio = st.number_input("Radio Advertising Spend ($)", min_value=0.0, value=250.0, step=5.0)
newspaper = st.number_input("Newspaper Advertising Spend ($)", min_value=0.0, value=100.0, step=5.0)

if st.button("Predict Sales"):
    # 3️⃣ Prepare input
    new_data = np.array([[tv, radio, newspaper]])
    new_data_poly = poly.transform(new_data)

    # 4️⃣ Make prediction
    predicted_sales = model.predict(new_data_poly)[0]

    # 5️⃣ Display results
    st.success(f"Predicted Sales: {predicted_sales:.2f} units")
