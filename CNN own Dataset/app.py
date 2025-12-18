import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import gdown
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="My Project Classifier", layout="centered")
st.title("🖼️ Image Classifier")
st.write("Upload an image to predict the class")

# --- CONSTANTS (YOUR DATA) ---
# Your Google Drive ID
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
# Your Model Filename
MODEL_PATH = 'Own_dataset_cnn_multi-class_classifier.h5'
# Download URL
URL = f'https://drive.google.com/uc?id={FILE_ID}'

# --- MODEL LOADER (With Caching) ---
@st.cache_resource
def load_model_safely():
    # 1. Download if not exists
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading model from Google Drive..."):
            gdown.download(URL, MODEL_PATH, quiet=False)

    # 2. Check for download failure (File too small)
    if os.path.exists(MODEL_PATH):
        if os.path.getsize(MODEL_PATH) < 10000: # < 10KB
            st.error("⚠️ Error: Model file download failed (Google Drive Quota). Please upload the .h5 file directly to GitHub.")
            st.stop()
            
    # 3. Load Model
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Load the model
model = load_model_safely()

if model:
    st.success("✅ Model Loaded Successfully!")

# --- PREDICTION LOGIC ---
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model is not None:
    # Display Image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Preprocessing
    # Note: Ensure (224, 224) matches your training input size
    img = image.load_img(uploaded_file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Create batch axis

    # Predict
    prediction = model.predict(img_array)
    predicted_index = np.argmax(prediction[0])
    
    # --- IMPORTANT: UPDATE THIS LIST ---
    # Replace these names with your actual folder names from training
    class_names = ['Class A', 'Class B', 'Class C', 'Class D']
    
    # Safety check for index
    if predicted_index < len(class_names):
        predicted_class = class_names[predicted_index]
        confidence = np.max(prediction[0]) * 100
        st.write(f"### 🎯 Prediction: **{predicted_class}**")
        st.write(f"Confidence: {confidence:.2f}%")
    else:
        st.warning(f"Predicted Index {predicted_index} is out of range for the class_names list.")
