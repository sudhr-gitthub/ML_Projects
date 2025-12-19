import streamlit as st
import numpy as np
import pickle

st.set_page_config(page_title="Fish Weight Prediction", layout="centered")

st.title("🐟 Fish Weight Prediction")
st.write("Predict fish weight using a **Polynomial Regression model**")

# Load trained model
with open("fish_poly_model.pkl", "rb") as f:
     model = pickle.load(f)

st.success("✅ Model loaded successfully")

st.subheader("Enter Fish Measurements")

l1 = st.number_input("Length1 (cm)", 0.0, 100.0, 20.0)
l2 = st.number_input("Length2 (cm)", 0.0, 100.0, 22.0)
l3 = st.number_input("Length3 (cm)", 0.0, 100.0, 25.0)
h  = st.number_input("Height (cm)",  0.0, 50.0,  6.0)
w  = st.number_input("Width (cm)",   0.0, 30.0,  4.0)

if st.button("Predict Weight"):
    input_data = np.array([[l1, l2, l3, h, w]])
    input_poly = transform(input_data)
    prediction = model.predict(input_poly)
    st.success(f"🐟 Predicted Fish Weight: **{prediction[0]:.2f} grams**")
