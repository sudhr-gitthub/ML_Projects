import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

st.set_page_config(page_title="CNN Classifier")
st.title("Image Classification App")

# --- MODEL CONFIG ---
# Link: https://drive.google.com/file/d/1E6-TihB-gCnDa910ZcwCFunW6xdoasmd/view?usp=sharing
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    # 1. Download if file is missing
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        with st.spinner("Downloading model..."):
            gdown.download(url, MODEL_FILENAME, quiet=False)

    # 2. Check file size (If < 2KB, download failed)
    if os.path.exists(MODEL_FILENAME):
        if os.path.getsize(MODEL_FILENAME) < 2000:
            st.error("Error: Model file is too small. Google Drive blocked the download.")
            st.stop()
            
    # 3. Load Model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

if model:
    st.success("Model loaded!")

# --- PREDICTION ---
file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if file is not None:
    image = Image.open(file)
    st.image(image, width=300)
    
    if model:
        # Resize to 224x224 (Standard)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image) / 255.0
        img_reshape = img_array[np.newaxis, ...]
        
        prediction = model.predict(img_reshape)
        
        # UPDATE THIS LIST
        class_names = ['Class 0', 'Class 1', 'Class 2', 'Class 3']
        
        idx = np.argmax(prediction[0])
        if idx < len(class_names):
            st.write(f"### Prediction: {class_names[idx]}")
        else:
            st.write(f"### Prediction Class Index: {idx}")
