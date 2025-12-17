import streamlit as st
import os

st.set_page_config(page_title="Debug Mode", layout="centered")
st.title("Diagnostic Mode: CNN Classifier")

# --- WRAPPER TO CATCH STARTUP ERRORS ---
try:
    import tensorflow as tf
    import numpy as np
    from PIL import Image, ImageOps
    import gdown
    import h5py

    st.write(f"TensorFlow Version: {tf.__version__}")
    st.write(f"NumPy Version: {np.__version__}")

    # --- 1. MODEL CONFIG ---
    # Link: https://drive.google.com/file/d/1E6-TihB-gCnDa910ZcwCFunW6xdoasmd/view?usp=sharing
    FILE_ID = '1E6-TihB-gCnDa910ZcwCFunW6xdoasmd'
    MODEL_FILENAME = 'Own_dataset_cnn_multi-class_classifier.h5'

    # --- 2. DOWNLOADER ---
    @st.cache_resource
    def load_model_file():
        if not os.path.exists(MODEL_FILENAME):
            url = f'https://drive.google.com/uc?id={FILE_ID}'
            st.warning(f"Attempting to download model from Drive ID: {FILE_ID}...")
            # quiet=False to see progress in logs
            gdown.download(url, MODEL_FILENAME, quiet=False)
        
        # Verify file
        if os.path.exists(MODEL_FILENAME):
            size = os.path.getsize(MODEL_FILENAME)
            st.success(f"File found! Size: {size/1024:.2f} KB")
            if size < 2000: # If less than 2KB, it's likely an error text file, not a model
                st.error("CRITICAL: File is too small. Google Drive likely blocked the download (Quota Exceeded).")
                st.stop()
        else:
            st.error("CRITICAL: Download failed completely.")
            st.stop()
            
        return MODEL_FILENAME

    model_path = load_model_file()

    # --- 3. MODEL LOADER ---
    # We load this outside the cache first to see if it crashes
    st.write("Attempting to load Keras model...")
    model = tf.keras.models.load_model(model_path)
    st.success("Model Loaded Successfully! App is ready.")

    # --- 4. PREDICTION LOGIC ---
    file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    if file is not None:
        image = Image.open(file)
        st.image(image, width=300)
        
        # Resize and Scale
        target_size = (224, 224) # Standard input size
        image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image)
        img_array = img_array / 255.0
        img_reshape = img_array[np.newaxis, ...]
        
        prediction = model.predict(img_reshape)
        st.write("Raw Prediction:", prediction)
        
        # Class names (Edit these!)
        class_names = ['Class A', 'Class B', 'Class C'] 
        idx = np.argmax(prediction[0])
        
        if idx < len(class_names):
            st.write(f"## Result: {class_names[idx]}")
        else:
            st.write(f"## Result: Class Index {idx}")

except Exception as e:
    # THIS IS THE IMPORTANT PART
    st.error("An error occurred during execution:")
    st.code(str(e))
    # Print detailed traceback in logs
    import traceback
    traceback.print_exc()
