import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="CNN Classifier", layout="centered")
st.title("CNN Multi-Class Image Classifier")
st.write("Upload an image to classify it using your custom model.")

# --- CONSTANTS ---
# Model file ID from your Google Drive link
FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

# --- MODEL LOADING LOGIC ---
@st.cache_resource
def load_model():
    # 1. Download the file if it doesn't exist
    if not os.path.exists(MODEL_FILENAME):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        with st.spinner("Downloading model from Google Drive..."):
            gdown.download(url, MODEL_FILENAME, quiet=False)

    # 2. Check if download was successful and valid
    if os.path.exists(MODEL_FILENAME):
        # Check file size. If < 2KB, it's likely a Google Drive error page, not the model.
        file_size = os.path.getsize(MODEL_FILENAME)
        if file_size < 2000: 
            st.error("Error: The model file downloaded is too small (likely a permission error). Please try uploading the .h5 file directly to GitHub instead.")
            st.stop()
    else:
        st.error("Error: Model file failed to download.")
        st.stop()

    # 3. Load the model
    try:
        model = tf.keras.models.load_model(MODEL_FILENAME)
        return model
    except Exception as e:
        st.error(f"Error loading Keras model: {e}")
        return None

# Load the model
model = load_model()

if model:
    st.success("Model loaded successfully!")

# --- PREDICTION LOGIC ---
file = st.file_uploader("Please upload an image file", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
    # 1. Resize (Update (224,224) if your model uses a different size like 150x150)
    size = (224, 224)    
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    
    # 2. Convert to Array & Normalize
    img = np.asarray(image)
    img = img / 255.0
    
    # 3. Reshape (1, Height, Width, Channels)
    img_reshape = img[np.newaxis, ...]
    
    # 4. Predict
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    if model:
        predictions = import_and_predict(image, model)
        
        # --- CLASS NAMES (YOU MUST EDIT THIS) ---
        # Update this list to match the folders in your dataset
        class_names = ['Class 0', 'Class 1', 'Class 2', 'Class 3'] 
        
        score = tf.nn.softmax(predictions[0])
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = 100 * np.max(score)
        
        st.write(f"## Prediction: {predicted_class}")
        st.write(f"Confidence: {confidence:.2f}%")
