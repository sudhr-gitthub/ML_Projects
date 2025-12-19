import streamlit as st
import pickle
import numpy as np
import os

st.set_page_config(page_title="Titanic Survival Prediction (SVM)", layout="centered")

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

# ---------------- Debug (optional) ----------------
# st.write("Model expects features:", model.n_features_in_)

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

# ---------------- Feature Orde
