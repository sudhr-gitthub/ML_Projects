import streamlit as st
import pickle
import numpy as np

# Page config
st.set_page_config(
    page_title="Stellar Classification",
    page_icon="🌌",
    layout="centered"
)

# Title
st.title("🌌 Stellar Object Classification")
st.write("Predict whether the object is a **Star**, **Galaxy**, or **QSO**")

# Load model
@st.cache_resource
def load_model():
    with open("stellar_classifier.pkl", "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()

# Sidebar inputs
st.sidebar.header("🔭 Input Astronomical Features")

u = st.sidebar.number_input("u (Ultraviolet)", value=18.0)
g = st.sidebar.number_input("g (Green)", value=17.0)
r = st.sidebar.number_input("r (Red)", value=16.5)
i = st.sidebar.number_input("i (Infrared)", value=16.0)
z = st.sidebar.number_input("z (Near Infrared)", value=15.8)
redshift = st.sidebar.number_input("Redshift", value=0.1)

# Predict button
if st.button("🚀 Predict"):
    input_data = np.array([[u, g, r, i, z, redshift]])
    prediction = model.predict(input_data)[0]

    label_map = {
        0: "🌟 Star",
        1: "🌌 Galaxy",
        2: "🌀 Quasar (QSO)"
    }

    st.success(f"### Prediction: {label_map.get(prediction, prediction)}")

# Footer
st.markdown("---")
st.caption("Built with Streamlit | Stellar Classification ML Project")
