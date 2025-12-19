import streamlit as st
import pickle
import numpy as np
import os

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="SVM Prediction App",
    layout="centered"
)

st.title("🔍 SVM Machine Learning Prediction App")
st.write("Enter feature values below to make a prediction using the trained SVM model.")

# ---------------- Load Model Safely ----------------
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, "SVM_train.pkl")

    with open(model_path, "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()
st.success("✅ SVM model loaded successfully")

# ---------------- Input Features ----------------
n_features = model.n_features_in_
st.subheader(f"Enter {n_features} Feature Values")

inputs = []
for i in range(n_features):
    value = st.number_input(
        f"Feature {i + 1}",
        value=0.0,
        format="%.4f"
    )
    inputs.append(value)

input_array = np.array(inputs).reshape(1, -1)

# ---------------- Prediction ----------------
if st.button("🔮 Predict"):
    prediction = model.predict(input_array)

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(input_array)
        st.success(f"🎯 Prediction: **{prediction[0]}**")
        st.info(f"📊 Confidence: **{np.max(probability) * 100:.2f}%**")
    else:
        st.success(f"🎯 Prediction: **{prediction[0]}**")

# ---------------- Footer ----------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit & SVM")
