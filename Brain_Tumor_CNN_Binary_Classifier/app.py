import streamlit as st
import tensorflow as st_tf
import numpy as np
from PIL import Image
import gdown
import os

# Set constants
IMG_SIZE = 256
MODEL_FILE = 'Train.h5'

# Google Drive File ID from your link
# Link: https://drive.google.com/file/d/1RUZzeRxgi4l_1_oCFFevKxJWQJxK8WhG/view?usp=sharing
FILE_ID = '1RUZzeRxgi4l_1_oCFFevKxJWQJxK8WhG'

@st.cache_resource
def load_model():
    # Check if model exists, if not, download it
    if not os.path.exists(MODEL_FILE):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        gdown.download(url, MODEL_FILE, quiet=False)
    
    # Load the model
    model = st_tf.keras.models.load_model(MODEL_FILE)
    return model

st.title("Brain Tumor Detection App")
st.write("Upload a brain MRI image to detect if a tumor is present.")

# Load the model (downloads automatically if needed)
with st.spinner('Loading model... (this may take a moment for the first download)'):
    try:
        model = load_model()
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    st.write("Classifying...")
    
    # Preprocess the image
    img = image.resize((IMG_SIZE, IMG_SIZE))
    img_array = st_tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    # Make prediction
    prediction = model.predict(img_array)
    confidence = prediction[0][0]
    
    # Display results
    if confidence > 0.5:
        st.error(f"**Tumor Detected**")
        st.write(f"Confidence: {confidence:.2%}")
    else:
        st.success(f"**Tumor Not Detected**")
        st.write(f"Confidence: {(1 - confidence):.2%}")
