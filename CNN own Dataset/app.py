import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np

# Set the title of the app
st.title("CNN Multi-Class Image Classifier")
st.write("Upload an image to classify it using your custom model.")

# Load the model with caching to prevent reloading on every run
@st.cache_resource
def load_model():
    # Load the specific model file from your drive
    model = tf.keras.models.load_model('Own_dataset_cnn_multi-class_classifier.h5')
    return model

# Load the model
try:
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
    # 1. Define the input size (e.g., (224, 224), (150, 150), (64, 64))
    target_size = (224, 224) 
    
    # 2. Resize and preprocess the image
    size = target_size
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    
    # Normalize the image (if you normalized by dividing by 255 during training)
    img = img / 255.0
    
    # Reshape the image to match model input shape: (1, height, width, channels)
    img_reshape = img[np.newaxis, ...]
    
    # Make prediction
    prediction = model.predict(img_reshape)
    return prediction

if file is not None:
    # Display the uploaded image
    image = Image.open(file)
    st.image(image, use_column_width=True)
    
    # Make prediction
    predictions = import_and_predict(image, model)
    
    # ---------------------------------------------------------
    # TODO: UPDATE THIS LIST WITH YOUR ACTUAL CLASS NAMES
    # ---------------------------------------------------------
    class_names = ['Class A', 'Class B', 'Class C', 'Class D'] # Replace with your actual labels
    
    # Get the class with the highest probability
    score = tf.nn.softmax(predictions[0])
    predicted_class = class_names[np.argmax(predictions[0])]
    confidence = 100 * np.max(score)
    
    st.write(f"## Prediction: {predicted_class}")
    st.write(f"Confidence: {confidence:.2f}%")
