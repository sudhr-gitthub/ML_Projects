import streamlit as st
import numpy as np
import joblib
from PIL import Image
import os

# --- Constants (must match training) ---
IMG_SIZE = 256
CURR_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(CURR_DIR, "Helmet_Classifier.pkl")
# --- Load Model ---
with open(MODEL_PATH, "rb") as file:
    model = joblib.load(file)
# --- App UI ---
st.set_page_config(page_title="Helmet Detection", layout="centered")
st.title("🪖 Helmet Detection System")
st.write("Upload an image to check whether a helmet is detected.")

# --- Image Upload ---
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # --- Preprocessing (MATCH ImageDataGenerator) ---
    img_array = np.array(image) / 255.0
    img_flattened = img_array.reshape(1, -1)

    # --- Prediction ---
    if st.button("Predict"):
        prediction = model.predict(img_flattened)[0]
        probability = model.predict_proba(img_flattened)[0][1]

        if prediction == 1:
            st.success(f"✅ Helmet Detected\n\nProbability: {probability:.2f}")
        else:
            st.error(f"⚠️ No Helmet Detected\n\nProbability: {1 - probability:.2f}")
