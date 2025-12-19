import streamlit as st
import pickle
import numpy as np

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="SVM Prediction App",
    layout="centered"
)

st.title("🔍 SVM Machine Learning Prediction App")
st.write("Enter feature values below to make a prediction using the trained SVM model.")

# ---------------- Load Model ----------------
@st.cache_resource
def load_model():
    with open("SVM_train.pkl", "rb") as file:
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
        label=f"Feature {i + 1}",
        value=0.0,
        format="%.4f"
    )
    inputs.append(value)

input_array = np.array(inputs).reshape(1, -1)

# ---------------- Prediction ----------------
if st.button("🔮 Predict"):
    prediction = model.predict(input_array)

    try:
        probability = model.predict_proba(input_array)
        st.success(f"🎯 Prediction: **{prediction[0]}**")
        st.info(f"📊 Confidence: **{np.max(probability) * 100:.2f}%**")
    except:
        st.success(f"🎯 Prediction: **{prediction[0]}**")

# ---------------- Footer ----------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit & SVM")
