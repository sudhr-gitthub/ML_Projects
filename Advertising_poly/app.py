# app.py
import streamlit as st
import pickle
import numpy as np
import os

st.set_page_config(
    page_title="Advertising Sales Predictor",
    layout="centered"
)

st.title("📊 Advertising Sales Prediction")
st.write(
    "Enter your advertising budget for TV, Radio, and Newspaper to predict sales."
)

# ---------------------------------
# 1️⃣ Load the trained model safely
# ---------------------------------
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "advertising_poly_model.pkl")

    with open(model_path, "rb") as f:
        model, poly = pickle.load(f)

    return model, poly

model, poly = load_model()

# ---------------------------------
# 2️⃣ User Inputs
# ---------------------------------
tv = st.number_input(
    "TV Advertising Spend ($)",
    min_value=0.0,
    value=500.0,
    step=10.0
)

radio = st.number_input(
    "Radio Advertising Spend ($)",
    min_value=0.0,
    value=250.0,
    step=5.0
)

newspaper = st.number_input(
    "Newspaper Advertising Spend ($)",
    min_value=0.0,
    value=100.0,
    step=5.0
)

# ---------------------------------
# 3️⃣ Prediction
# ---------------------------------
if st.button("🔮 Predict Sales"):
    try:
        # Prepare input
        new_data = np.array([[tv, radio, newspaper]])

        # Polynomial transformation
        new_data_poly = poly.transform(new_data)

        # Prediction
        predicted_sales = model.predict(new_data_poly)[0]

        # Output
        st.success(f"📈 Predicted Sales: **{predicted_sales:.2f} units**")

    except Exception as e:
        st.error("Prediction failed. Please check the model format.")
        st.exception(e)
