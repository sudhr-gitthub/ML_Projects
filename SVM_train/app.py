import streamlit as st
import pickle
import numpy as np
import os

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Titanic Survival Prediction (SVM)",
    layout="centered"
)

st.title("🚢 Titanic Survival Prediction (SVM Model)")
st.write("Enter passenger details to predict survival")

# ---------------- Load Model ----------------
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "SVM_train.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

model = load_model()
st.success("✅ Model loaded successfully")

# ---------------- Inputs (MATCH TRAINING) ----------------
st.subheader("Passenger Information")

passenger_id = st.number_input("Passenger ID", min_value=1, value=1)
pclass = st.selectbox("Passenger Class", [1, 2, 3])
sex = st.selectbox("Sex", ["Male", "Female"])
age = st.number_input("Age", min_value=0.0, max_value=100.0, value=25.0)
sibsp = st.number_input("Siblings / Spouses aboard", min_value=0, value=0)
parch = st.number_input("Parents / Children aboard", min_value=0, value=0)
fare = st.number_input("Fare", min_value=0.0, value=10.0)
embarked = st.selectbox("Embarked Port", ["C", "Q", "S"])

# ---------------- Encoding (MUST match training) ----------------
sex_encoded = 0 if sex == "Male" else 1
embarked_map = {"C": 1, "Q": 2, "S": 3}
embarked_encoded = embarked_map[embarked]

# ---------------- Feature Order (VERY IMPORTANT) ----------------
input_data = np.array([
    passenger_id,
    pclass,
    sex_encoded,
    age,
    sibsp,
    parch,
    fare,
    embarked_encoded
]).reshape(1, -1)

# ---------------- Prediction & Output ----------------
if st.button("🔮 Predict Survival"):
    prediction = model.predict(input_data)[0]

    st.subheader("🔍 Prediction Result")

    # Show raw output (for checking)
    st.write("Model Output (0 = Not Survived, 1 = Survived):", prediction)

    if prediction == 1:
        st.success("✅ Passenger is **LIKELY TO SURVIVE**")
    else:
        st.error("❌ Passenger is **NOT LIKELY TO SURVIVE**")

    # Optional probability (only if supported)
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(input_data)
        st.info(f"🧮 Survival Probability: **{prob[0][1]*100:.2f}%**")

# ---------------- Footer ----------------
st.markdown("---")
st.caption("SVM Classification Model | Titanic Dataset")
