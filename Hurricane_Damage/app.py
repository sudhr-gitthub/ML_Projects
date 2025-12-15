import streamlit as st
import numpy as np
import pickle
from PIL import Image
import os

# --- Page Config ---
st.set_page_config(page_title="Hurricane Damage Detection", layout="centered")

# --- Model Loading ---
@st.cache_resource
def load_model():
    # Helper to get absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for likely model names
    possible_names = ['model.pkl', 'hurricane.pkl', 'hurricane_damage.pkl', 'wildfire.pkl']
    model_path = None
    
    for name in possible_names:
        temp_path = os.path.join(current_dir, name)
        if os.path.exists(temp_path):
            model_path = temp_path
            break
            
    if model_path is None:
        st.error("❌ Model not found.")
        st.warning("Please upload your model file (e.g., 'model.pkl') to the GitHub repository folder.")
        return None

    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- App Interface ---
st.title("URC: Hurricane Damage Assessment")
st.markdown("Upload a satellite image to detect if a building has sustained damage.")

uploaded_file = st.file_uploader("Choose a satellite image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. Display Image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # 2. Preprocess Image
    # (Resize to match the training data - typically 100x100 or 128x128 for these projects)
    # We will assume 100x100 flattened based on standard Sudhanshu/iNeuron projects
    st.write("Analyzing...")
    
    try:
        # Resize to typical training size
        img_resized = image.resize((100, 100)) 
        
        # Convert to numpy array
        img_array = np.array(img_resized)
        
        # Flatten the image (Height * Width * Channels) -> 1D Array
        # If the model expects flattened input:
        if len(img_array.shape) == 3:
            flattened_img = img_array.flatten().reshape(1, -1)
        else:
            # Handle grayscale
            flattened_img = img_array.flatten().reshape(1, -1)

        # 3. Predict
        if st.button("Detect Damage"):
            if model is not None:
                prediction = model.predict(flattened_img)
                
                # Result Logic
                # Assuming 0 = No Damage, 1 = Damage (or 'damage'/'no_damage' strings)
                result = prediction[0]
                
                st.subheader("Assessment Result:")
                if str(result).lower() in ['1', 'damage', 'yes']:
                    st.error("⚠️ DAMAGE DETECTED")
                    st.write("This structure appears to have sustained damage.")
                else:
                    st.success("✅ NO DAMAGE")
                    st.write("This structure appears intact.")
            else:
                st.error("Model is not loaded.")
                
    except Exception as e:
        st.error(f"Error during processing: {e}")
        st.info("Ensure the image is valid and the model expects 100x100 pixel input.")

# --- Sidebar Info ---
st.sidebar.title("About")
st.sidebar.info(
    "This app uses Machine Learning to classify post-hurricane satellite imagery."
)
