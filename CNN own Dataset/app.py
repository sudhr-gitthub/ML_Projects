import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import gdown
import os

# Set the title of the app
st.title("CNN Multi-Class Image Classifier")
st.write("Upload an image to classify it using your custom model.")

# Define the Google Drive file ID and output filename
# Derived from your link: https://drive.google.com/file/d/1E6-TihB-gCnDa910ZcwCFunW6xdoasmd/view?usp=sharing
file_id = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
model_file = 'Own_dataset_cnn_multi-class_classifier.h5'

@st.cache_resource
def load_model():
    # Check if the file already exists locally; if not, download it
    if not os.path.exists(model_file):
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, model_file, quiet=False)
    
    # Load the model
    model = tf.keras.models.load_model(model_file)
    return model

# Load the model with error handling
try:
    with st.spinner('Downloading model from Google Drive... this may take a minute...'):
        model = load_model()
    st.success("Model loaded successfully!")
except Exception as e:
    st.error(f"Error loading model: {e}")

# Upload image widget
file = st.file_uploader("Please upload an image file", type=["jpg", "png", "jpeg"])

def import_and_predict(image_data, model):
    # ---------------------------------------------------------
    # TODO: UPDATE THESE VALUES TO MATCH YOUR MODEL'S TRAINING
    # ---------------------------------------------------------
    # 1. Define the input size used during training
    target_size = (224, 224) 
    
    # 2. Resize and preprocess
    image = ImageOps.fit(image_data, target_size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    
    # Normalize (Standard for most CNNs)
    img = img / 255.0
    
    # Reshape for model input: (1, height, width, channels)
    img_reshape = img[np.newaxis, ...]
    
    # Predict
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    if model:
        predictions = import_and_predict(image, model)
        
        # ---------------------------------------------------------
        # TODO: UPDATE THIS LIST WITH YOUR ACTUAL CLASS NAMES
        # ---------------------------------------------------------
        class_names = ['Class A', 'Class B', 'Class C'] 
        
        # Interpret results
        score = tf.nn.softmax(predictions[0])
        
        # Check if class_names matches prediction output shape
        if len(class_names) == len(predictions[0]):
            predicted_class = class_names[np.argmax(predictions[0])]
            confidence = 100 * np.max(score)
            st.write(f"## Prediction: {predicted_class}")
            st.write(f"Confidence: {confidence:.2f}%")
        else:
            st.error(f"Error: Model predicted {len(predictions[0])} classes, but you defined {len(class_names)} names in the code.")
