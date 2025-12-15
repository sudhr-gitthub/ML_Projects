import streamlit as st
import numpy as np
import joblib
from PIL import Image
import os

# --- Page Config ---
st.set_page_config(page_title="Hurricane Damage Detection", layout="centered")

# --- Model Loading ---
@st.cache_resource
def load_model():
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of possible names for your model file
    possible_names = ['model.pkl', 'hurricane.pkl', 'hurricane_damage.pkl', 'hurricane_classifier.pkl']
    model_path = None
    
    # Search for the file
    for name in possible_names:
        temp_path = os.path.join(current_dir, name)
        if os.path.exists(temp_path):
            model_path = temp_path
            break
            
    if model_path is None:
        st.error("❌ Model not found.")
        st.warning("Please upload your model file (e.g., 'model.pkl') to the GitHub repository.")
        return None

    try:
        # USE JOBLIB INSTEAD OF PICKLE (Fixes the '\x03' error)
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        # Check if it's a Git LFS pointer (common issue)
        try:
            with open(model_path, "r", errors='ignore') as f:
                content = f.read(50)
            if "version https://git-lfs" in content:
                st.error("⚠️ It looks like you uploaded a Git LFS pointer, not the actual file.")
        except:
            pass
        return None

model = load_model()

# --- App Interface ---
st.title("URC: Hurricane Damage Assessment")
st.markdown("Upload a satellite image to detect if a building has sustained damage.")

uploaded_file = st.file_uploader("Choose a satellite image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # 1. Display Image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        st.write("Analyzing...")
        
        # 2. Preprocess Image (Resize to 100x100 and Flatten)
        # This matches standard ML project formats
        img_resized = image.resize((100, 100)) 
        img_array = np.array(img_resized)
        
        # Flatten: (100, 100, 3) -> (1, 30000)
        if len(img_array.shape) == 3:
            flattened_img = img_array.flatten().reshape(1, -1)
        else:
            # Handle grayscale images if necessary
            flattened_img = img_array.flatten().reshape(1, -1)

        # 3. Predict
        if st.button("Detect Damage", type="primary"):
            if model is not None:
                prediction = model.predict(flattened_img)
                
                # Result Logic
                result = prediction[0]
                
                st.subheader("Assessment Result:")
                # Check for various "Damage" indicators (1, '1', 'damage', 'yes')
                if str(result).lower() in ['1', 'damage', 'yes', 'true']:
                    st.error("⚠️ DAMAGE DETECTED")
                    st.write("This structure appears to have sustained damage.")
                else:
                    st.success("✅ NO DAMAGE")
                    st.write("This structure appears intact.")
            else:
                st.error("Model is not loaded. Please check the sidebar/logs.")
                
    except Exception as e:
        st.error(f"Error during processing: {e}")
        st.info("Ensure the model expects a flattened 100x100 pixel image.")

# --- Sidebar Info ---
st.sidebar.title("About")
st.sidebar.info("This app uses Machine Learning to classify post-hurricane satellite imagery.")
