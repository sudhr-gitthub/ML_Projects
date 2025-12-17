import streamlit as st
import pickle
import numpy as np
import pandas as pd
import requests
import io

# --- Configuration ---
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/Marketing_Campaign_ID_KNN/"

st.set_page_config(page_title="Campaign Predictor", layout="centered")

st.title("🎯 Marketing Campaign Predictor")
st.markdown("Predict if a customer will accept a marketing offer based on 5 key details.")

# --- Helper Functions ---
@st.cache_resource
def load_file_from_github(filename):
    """Fetches a pickle file from the specific GitHub path."""
    url = BASE_URL + filename
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pickle.load(io.BytesIO(response.content))
    except Exception:
        return None

# --- Sidebar: Model & Scaler Loading ---
st.sidebar.header("⚙️ Configuration")
data_source = st.sidebar.radio("Load files from:", ["GitHub (Auto)", "Upload Manually"])

model = None
scaler = None

if data_source == "GitHub (Auto)":
    with st.spinner("Fetching model and scaler from GitHub..."):
        model = load_file_from_github("knn_model.pkl")
        scaler = load_file_from_github("scaler.pkl") # Assuming standard name
        
        if model:
            st.sidebar.success("✅ Model loaded from GitHub")
        else:
            st.sidebar.error("❌ Model not found on GitHub")

        if scaler:
            st.sidebar.success("✅ Scaler loaded from GitHub")
        else:
            st.sidebar.warning("⚠️ 'scaler.pkl' not found on GitHub.")

elif data_source == "Upload Manually":
    model_file = st.sidebar.file_uploader("Upload knn_model.pkl", type=['pkl'])
    scaler_file = st.sidebar.file_uploader("Upload scaler.pkl", type=['pkl'])
    
    if model_file:
        model = pickle.load(model_file)
        st.sidebar.success("✅ Model uploaded")
    if scaler_file:
        scaler = pickle.load(scaler_file)
        st.sidebar.success("✅ Scaler uploaded")

# --- Main App Logic ---
if model:
    # 1. Collect Inputs (Only the 5 most important ones)
    st.subheader("Customer Information")
    col1, col2 = st.columns(2)
    
    with col1:
        income = st.number_input("Income ($)", value=52000.0, step=1000.0)
        age = st.number_input("Age", value=35, min_value=18, max_value=100)
        recency = st.number_input("Recency (Days since last purchase)", value=49, min_value=0)
    
    with col2:
        kidhome = st.number_input("Kids at Home", value=0, min_value=0)
        teenhome = st.number_input("Teens at Home", value=0, min_value=0)

    if st.button("Predict Outcome", type="primary"):
        try:
            # 2. Prepare the full input array (16 features)
            # The model expects 16 features. We fill the missing 11 with '0.0'
            # because in scaled data, 0.0 represents the average/mean value.
            
            # Feature order must match training: 
            # Income, Age, Kidhome, Teenhome, Recency, [11 other features...]
            
            # Create array of zeros (average values)
            full_input = np.zeros((1, 16))
            
            # Update the known features
            # Indices based on training data order: 0=Income, 1=Age, 2=Kid, 3=Teen, 4=Recency
            full_input[0, 0] = income
            full_input[0, 1] = age
            full_input[0, 2] = kidhome
            full_input[0, 3] = teenhome
            full_input[0, 4] = recency

            # 3. Apply Scaling (CRITICAL STEP)
            final_input = full_input
            if scaler:
                # Transform the raw input using the loaded scaler
                final_input = scaler.transform(full_input)
            else:
                st.warning("⚠️ No scaler detected. Prediction might be inaccurate using raw data.")

            # 4. Predict
            prediction = model.predict(final_input)
            
            st.divider()
            if prediction[0] == 1:
                st.success("### ✅ Result: Customer will likely ACCEPT the offer.")
            else:
                st.error("### ❌ Result: Customer will likely REJECT the offer.")

        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.info("Ensure you have uploaded both the Model and the Scaler.")

else:
    st.info("👈 Please load the model to start.")
