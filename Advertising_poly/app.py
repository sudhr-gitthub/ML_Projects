import streamlit as st
import pickle
import numpy as np
import os

# ----------------------------------
# Load model using absolute path
# ----------------------------------
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "advertising_poly_model.pkl")

    with open(model_path, "rb") as file:
        model = pickle.load(file)

    return model

model = load_model()

# ----------------------------------
# Streamlit UI
# ----------------------------------
st.set_page_config(
    page_title="Advertising Sales Prediction",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Advertising Sales Prediction")
st.write("Predict Sales using Polynomial Regression")

# Inputs
tv = st.number_input("TV Advertising Spend", min_value=0.0, step=1.0)
radio = st.number_input("Radio Advertising Spend", min_value=0.0, step=1.0)
newspaper = st.number_input("Newspaper Advertising Spend", min_value=0.0, step=1.0)

if st.button("🔮 Predict Sales"):
    X = np.array([[tv, radio, newspaper]])
    prediction = model.predict(X)
    st.success(f"📊 Predicted Sales: **{prediction[0]:.2f}**")
