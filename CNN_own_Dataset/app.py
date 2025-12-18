import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

st.set_page_config(page_title="Image Classifier", layout="centered")
st.title("Image Classification App")

# --- 1. SETUP MODEL PATHS ---
# Google Drive File ID
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
# The file to save locally
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'
# Download Link
URL = f'https://drive.google.com/uc?id={FILE_ID}'

# --- 2. DOWNLOAD & LOAD MODEL ---
@st.cache_resource
def load_model():
    # A. Download if missing
    if not os.path.exists(MODEL_FILENAME):
        with st.spinner("Downloading model... (This may take a minute)"):
            gdown.download(URL, MODEL_FILENAME, quiet=False)

    # B. Validate File
    if os.path.exists(MODEL_FILENAME):
        # If file is < 10KB, it's an error file, not the model
        if os.path.getsize(MODEL_FILENAME) < 10000:
            st.error("Error: Model file is too small. Google Drive blocked the download.")
            st.stop()
            
    # C. Load Keras Model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

if model:
    st.success("Model loaded successfully!")

# --- 3. PREDICTION ---
file = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])

if file is not None and model is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    # Resize to 224x224 (Standard)
    size = (224, 224)    
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img_array = np.asarray(image) / 255.0
    img_reshape = img_array[np.newaxis, ...]
    
    prediction = model.predict(img_reshape)
    
    # UPDATE THESE NAMES TO MATCH YOUR DATASET
    class_names = ['Class A', 'Class B', 'Class C', 'Class D']
    
    predicted_index = np.argmax(prediction[0])
    if predicted_index < len(class_names):
        st.write(f"### Prediction: {class_names[predicted_index]}")
    else:
        st.write(f"Prediction Index: {predicted_index}")
