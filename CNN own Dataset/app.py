import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

st.set_page_config(page_title="CNN Classifier", layout="centered")

st.title("Image Classification App")

# --- MODEL CONFIGURATION ---
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    # 1. Download file if missing
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        # quiet=False allows us to see download progress in logs
        gdown.download(url, MODEL_FILENAME, quiet=False)

    # 2. CHECK FILE SIZE (Crucial Step)
    # If the file is < 10KB, it's likely a Google Drive error page, not the model.
    if os.path.exists(MODEL_FILENAME):
        size = os.path.getsize(MODEL_FILENAME)
        if size < 10000:
            st.error("CRITICAL ERROR: The downloaded file is too small. Google Drive refused the automated download.")
            st.warning("SOLUTION: Download the .h5 file manually and upload it directly to your GitHub repository.")
            st.stop()
    
    # 3. Load Model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Error loading Keras model: {e}")
        return None

# Load the model
with st.spinner("Setting up model..."):
    model = load_model()

if model:
    st.success("Model loaded successfully!")

# --- PREDICTION ---
file = st.file_uploader("Upload an image...", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
    # Resize to 224x224 (Standard)
    size = (224, 224)    
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    img = img / 255.0
    img_reshape = img[np.newaxis, ...]
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    if model:
        predictions = import_and_predict(image, model)
        
        # --- UPDATE YOUR CLASS NAMES HERE ---
        class_names = ['Class A', 'Class B', 'Class C', 'Class D']
        
        score = tf.nn.softmax(predictions[0])
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = 100 * np.max(score)
        
        st.write(f"### Result: {predicted_class}")
        st.write(f"Confidence: {confidence:.2f}%")
