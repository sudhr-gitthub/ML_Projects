import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Image Classifier", layout="centered")

st.title("Image Classification App")
st.write("Upload an image to classify it.")

# --- MODEL SETTINGS ---
# Extracted from your link: https://drive.google.com/file/d/1E6-TihB-gCnDa910ZcwCFunW6xdoasmd/view?usp=sharing
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    # 1. Check if model exists locally
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        with st.spinner("Downloading model from Google Drive... (This happens only once)"):
            gdown.download(url, MODEL_FILENAME, quiet=False)

    # 2. Verify file size (Small files usually mean download failed/permission error)
    if os.path.exists(MODEL_FILENAME):
        file_size = os.path.getsize(MODEL_FILENAME)
        if file_size < 10000:  # Less than 10KB
            st.error("Error: The downloaded model file is too small. This usually means Google Drive blocked the automated download.")
            st.stop()
    else:
        st.error("Error: Model file failed to download.")
        st.stop()

    # 3. Load the model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Load model (cached)
model = load_model()

if model:
    st.success("Model ready! 🚀")

# --- IMAGE PROCESSING & PREDICTION ---
file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
    # Resize to 224x224 (Standard for most models - Change if yours is different)
    size = (224, 224)    
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    
    # Convert to array
    img = np.asarray(image)
    
    # Normalize pixel values (0-1)
    img = img / 255.0
    
    # Reshape for the model (1, 224, 224, 3)
    img_reshape = img[np.newaxis, ...]
    
    # Predict
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    if st.button("Classify Image"):
        if model:
            predictions = import_and_predict(image, model)
            
            # --- CLASS NAMES ---
            # IMPORTANT: You must update this list to match your specific classes!
            class_names = ['Class A', 'Class B', 'Class C', 'Class D'] 
            
            score = tf.nn.softmax(predictions[0])
            
            # Display Result
            if len(predictions[0]) > len(class_names):
                st.warning(f"Model predicted {len(predictions[0])} classes, but you only listed {len(class_names)} names. Please update 'class_names' in app.py.")
                st.write(f"Raw Prediction: {predictions}")
            else:
                predicted_class = class_names[np.argmax(predictions[0])]
                confidence = 100 * np.max(score)
                st.write(f"### Prediction: {predicted_class}")
                st.write(f"Confidence: {confidence:.2f}%")
