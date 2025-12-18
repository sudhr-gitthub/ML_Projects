import streamlit as st
import pickle
import numpy as np
import os

@st.cache_resource
def load_model():
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "advertising_poly_model.pkl")
    with open(model_path, "rb") as f:
        return pickle.load(f)

model = load_model()

st.title("📈 Advertising Sales Prediction")
st.write("Predict Sales using Polynomial Regression")

tv = st.number_input("TV Advertising Spend", min_value=0.0, step=1.0)
radio = st.number_input("Radio Advertising Spend", min_value=0.0, step=1.0)
newspaper = st.number_input("Newspaper Advertising Spend", min_value=0.0, step=1.0)

if st.button("🔮 Predict Sales"):
    X = np.array([[tv, radio, newspaper]])

    try:
        # ✅ CASE 1: Pipeline
        if hasattr(model, "predict"):
            y_pred = model.predict(X)

        # ✅ CASE 2: Tuple (poly, regressor)
        elif isinstance(model, tuple):
            poly, regressor = model
            X_poly = poly.transform(X)
            y_pred = regressor.predict(X_poly)

        # ✅ CASE 3: Dictionary
        elif isinstance(model, dict):
            X_poly = model["poly"].transform(X)
            y_pred = model["model"].predict(X_poly)

        else:
            raise ValueError("Unknown model format")

        st.success(f"📊 Predicted Sales: **{y_pred[0]:.2f}**")

    except Exception as e:
        st.error("Prediction failed due to model structure mismatch")
        st.exception(e)
