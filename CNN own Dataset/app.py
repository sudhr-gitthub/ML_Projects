import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

st.set_page_config(page_title="CNN Classifier")
st.title("CNN Multi-Class Image Classifier")

# --- 1. MODEL CONFIG ---
# Link: https://drive.google.com/file/d/1E6-TihB-gCnDa910ZcwCFunW6xdoasmd/view?usp=sharing
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        # quiet=False helps debug download issues
        gdown.download(url, MODEL_FILENAME, quiet=False)
    
    # Load model
    model = tf.keras.models.load_model(MODEL_FILENAME)
    return model

# Load the model
try:
    with st.spinner('Downloading and loading model...'):
        model = load_model()
    st.success("Model loaded!")
except Exception as e:
    st.error(f"Error loading model: {e}")

# --- 2. PREDICTION ---
file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
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
        class_names = ['Class 0', 'Class 1', 'Class 2', 'Class 3'] # UPDATE THIS
        
        score = tf.nn.softmax(predictions[0])
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = 100 * np.max(score)
        
        st.write(f"## Prediction: {predicted_class}")
        st.write(f"Confidence: {confidence:.2f}%")
