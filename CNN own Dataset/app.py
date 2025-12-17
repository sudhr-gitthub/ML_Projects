import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

# Set page config
st.set_page_config(page_title="CNN Classifier", layout="centered")

st.title("CNN Multi-Class Image Classifier")
# Google Drive File ID
file_id = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
model_file = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    if not os.path.exists(model_file):
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, model_file, quiet=False)
    
    model = tf.keras.models.load_model(model_file)
    return model

@st.cache_resource
def load_model():
    # 1. Download if not exists
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        st.info(f"Downloading model from Google Drive (ID: {FILE_ID})...")
        gdown.download(url, MODEL_FILENAME, quiet=False)

    # 2. Check if file is valid (larger than 1KB)
    if os.path.exists(MODEL_FILENAME):
        file_size = os.path.getsize(MODEL_FILENAME)
        if file_size < 1000: # Less than 1KB means it's likely a corruption/error file
            st.error("Error: The downloaded model file is too small. It might be a Google Drive permission error.")
            st.stop()
    else:
        st.error("Error: Model file failed to download.")
        st.stop()

    # 3. Load Model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Critical Error loading model: {e}")
        st.stop()
        return None

# Load the model
model = load_model()

if model:
    st.success("Model loaded successfully!")

# Upload image
file = st.file_uploader("Please upload an image file", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
    # Resize to the size your model expects (224x224 is common, but change if yours is 180x180 etc)
    size = (224, 224)    
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    
    # Normalize
    img = img / 255.0
    
    # Reshape
    img_reshape = img[np.newaxis, ...]
    
    # Predict
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    if model:
        predictions = import_and_predict(image, model)
        
        # --- CLASS NAMES ---
        # YOU MUST EDIT THIS LIST TO MATCH YOUR TRAINING FOLDER NAMES
        class_names = ['Class 0', 'Class 1', 'Class 2', 'Class 3'] 
        
        score = tf.nn.softmax(predictions[0])
        
        # Safe prediction display
        if len(predictions[0]) <= len(class_names):
            predicted_class = class_names[np.argmax(predictions[0])]
            confidence = 100 * np.max(score)
            st.write(f"## Prediction: {predicted_class}")
            st.write(f"Confidence: {confidence:.2f}%")
        else:
            st.write(f"## Prediction Raw Output: {predictions}")
            st.warning(f"Model predicted {len(predictions[0])} classes, but you only defined {len(class_names)} in the 'class_names' list. Please update line 78 in app.py.")
