import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

st.set_page_config(page_title="Classifier", layout="centered")
st.title("Image Classifier")

# Google Drive ID
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        gdown.download(url, MODEL_FILENAME, quiet=False)
    
    # Check if download succeeded (File > 10KB)
    if os.path.exists(MODEL_FILENAME) and os.path.getsize(MODEL_FILENAME) > 10000:
        return tf.keras.models.load_model(MODEL_FILENAME)
    return None

with st.spinner("Loading Model..."):
    model = load_model()

if model is None:
    st.error("Error: Model failed to download from Google Drive.")
else:
    st.success("Model Ready!")
    
    file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    if file:
        image = Image.open(file)
        st.image(image, width=300)
        
        # Preprocessing
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img = np.asarray(image) / 255.0
        img_reshape = img[np.newaxis, ...]
        
        prediction = model.predict(img_reshape)
        st.write(f"Raw Prediction: {prediction}")
