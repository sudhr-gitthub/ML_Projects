import streamlit as st
import tensorflow as st_tf
import numpy as np
from PIL import Image

# Set constants matching the training configuration
IMG_SIZE = 256

# Load the model
# Cache the model loading to prevent reloading on every interaction
@st.cache_resource
def load_model():
    # Make sure 'Train.h5' is in the same directory or provide the full path
    model = st_tf.keras.models.load_model('Train.h5')
    return model

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}. Please ensure 'Train.h5' is in the directory.")
    st.stop()

st.title("Brain Tumor Detection App")
st.write("Upload a brain MRI image to detect if a tumor is present.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    st.write("Classifying...")
    
    # Preprocess the image to match the training format
    # 1. Resize the image to (256, 256)
    img = image.resize((IMG_SIZE, IMG_SIZE))
    
    # 2. Convert to array
    img_array = st_tf.keras.utils.img_to_array(img)
    
    # 3. Expand dimensions to match batch shape (1, 256, 256, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    # 4. Rescale pixel values (1./255) as done in ImageDataGenerator
    img_array = img_array / 255.0
    
    # Make prediction
    prediction = model.predict(img_array)
    
    # Logic from the notebook:
    # value > 0.5 implies Tumor Detected
    # value <= 0.5 implies Tumor Not Detected
    confidence = prediction[0][0]
    
    if confidence > 0.5:
        st.error(f"**Tumor Detected**")
        st.write(f"Confidence: {confidence:.2%}")
    else:
        st.success(f"**Tumor Not Detected**")
        st.write(f"Confidence: {(1 - confidence):.2%}")
