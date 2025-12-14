# ML_Projects/alzheimer/app.py

import streamlit as st
import numpy as np
import joblib
from PIL import Image
from pathlib import Path

# --- Configuration Constants (Must match training) ---
IMG_SIZE = 256
MODEL_FILE_NAME = "alzheimers_logreg.pkl"
# Note: Ensure IMG_SIZE matches the dimensions used for training the model 
# before flattening it for the Logistic Regression classifier.

# --- Robust and Silent Model Loading ---
@st.cache_resource(show_spinner=False)
def load_model():
    """
    Loads the machine learning model silently using an absolute path.
    Errors will still be displayed if the file is missing or corrupted.
    """
    
    # Get the directory of the current script (app.py)
    BASE_DIR = Path(__file__).resolve().parent
    
    # Construct the full path to the model file
    model_path = BASE_DIR / MODEL_FILE_NAME
    file_path = str(model_path)
    
    try:
        # Load the model without printing success or info messages to the UI
        model = joblib.load(file_path)
        return model
    except FileNotFoundError:
        st.error(f"FATAL ERROR: Model file not found at: {file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        st.stop()

# Load the model once
model = load_model()

# --- App UI and Logic ---
st.set_page_config(page_title="Alzheimer's Detection", layout="centered")

st.title("Alzheimer's Disease Detection (Logistic Regression)")
st.write("Upload a brain MRI image to predict Alzheimer's presence.")

# Image Upload
uploaded_file = st.file_uploader(
    "Upload Brain MRI Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    
    # 1. Load and Resize Image
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # 2. Preprocessing (MUST MATCH TRAINING)
    # Convert to array and scale (0-1)
    img_array = np.array(image) / 255.0
    
    # Flatten the image array (256*256*3 features) for Logistic Regression
    # The shape must be (1, N_FEATURES) where N_FEATURES = IMG_SIZE * IMG_SIZE * 3
    img_flattened = img_array.reshape(1, -1)
    
    st.markdown("---")
    
    # 3. Prediction
    if st.button("Predict"):
        with st.spinner('Analyzing MRI scan...'):
            try:
                # Predict the class (0 or 1)
                prediction = model.predict(img_flattened)[0]
                
                # Predict the probability of the positive class (assuming 1 is Alzheimer's)
                # [0] refers to the first (and only) sample, [1] refers to the probability of class 1.
                probability = model.predict_proba(img_flattened)[0][1]
                
                st.subheader("Prediction Result:")
                
                if prediction == 1:
                    st.error(f"🔴 **Alzheimer's Detected**\n\nProbability (of Alzheimer's): **{probability:.2f}**")
                else:
                    st.success(f"🟢 **No Alzheimer's Detected**\n\nProbability (of No Alzheimer's): **{1 - probability:.2f}**")
                    
                st.markdown("---")
                st.info("Note: This is a classification based on a Logistic Regression model and should not replace professional medical advice.")

            except Exception as e:
                st.error(f"An error occurred during prediction. Check if your model expects a different input format: {e}")
