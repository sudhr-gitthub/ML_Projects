import streamlit as st
import pickle
import numpy as np
import requests
import io

# --- Configuration ---
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
# Base URL for fetching files
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/Marketing_Campaign_ID_KNN/"

st.set_page_config(page_title="Marketing Campaign AI", layout="centered")

st.title("🚀 Marketing Campaign Predictor")
st.markdown("Predict customer response using the KNN AI Model.")

# --- Helper: Load Files ---
@st.cache_resource
def load_file_from_github(filename):
    try:
        response = requests.get(BASE_URL + filename)
        response.raise_for_status()
        return pickle.load(io.BytesIO(response.content))
    except:
        return None

# --- Custom Scaler (The Fix) ---
class FallbackScaler:
    """
    If the real scaler.pkl is missing, this class estimates the scaling
    based on the standard 'Marketing Campaign' dataset statistics.
    This prevents the app from breaking.
    """
    def transform(self, X):
        # Stats extracted from the standard dataset for these features
        # Order: [Income, Age, Kidhome, Teenhome, Recency, ...others...]
        means = np.array([52247.0, 51.0, 0.44, 0.51, 49.0]) 
        stds  = np.array([25173.0, 17.0, 0.54, 0.54, 29.0])
        
        # Scale the first 5 columns (the ones we ask the user for)
        X_copy = X.copy()
        for i in range(5):
            X_copy[:, i] = (X[:, i] - means[i]) / stds[i]
            
        return X_copy

# --- Load Resources ---
with st.spinner("Connecting to GitHub Model..."):
    model = load_file_from_github("knn_model.pkl")
    scaler = load_file_from_github("scaler.pkl")

# If GitHub scaler is missing, use the fallback
if scaler is None:
    scaler = FallbackScaler()
    st.toast("⚠️ Using fallback scaler (standard stats)", icon="ℹ️")

# --- UI Layout ---
if model:
    st.success("✅ Model System Online")
    
    st.subheader("Customer Profile")
    
    # Input columns
    col1, col2 = st.columns(2)
    
    with col1:
        income = st.number_input("Income ($)", value=85000.0, step=1000.0, help="Higher income increases acceptance chance.")
        age = st.number_input("Age", value=45, min_value=18, max_value=90)
        recency = st.number_input("Days Since Last Purchase", value=10, min_value=0, help="Lower number is better.")

    with col2:
        kidhome = st.number_input("Kids at Home", value=0, min_value=0)
        teenhome = st.number_input("Teens at Home", value=0, min_value=0)

    # --- Prediction ---
    if st.button("Predict Result", type="primary"):
        try:
            # 1. Prepare Input Array (16 features total)
            # We fill the 5 known features and leave the rest as 0 (average)
            input_features = np.zeros((1, 16))
            
            input_features[0, 0] = income
            input_features[0, 1] = age
            input_features[0, 2] = kidhome
            input_features[0, 3] = teenhome
            input_features[0, 4] = recency
            
            # 2. Scale the data
            scaled_features = scaler.transform(input_features)
            
            # 3. Predict
            prediction = model.predict(scaled_features)
            
            st.divider()
            
            if prediction[0] == 1:
                st.success("### 🎉 Prediction: ACCEPT")
                st.write("This customer fits the profile of a high-value target.")
            else:
                st.error("### ❌ Prediction: REJECT")
                st.write("This customer is unlikely to accept the offer.")

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.error("Could not load 'knn_model.pkl'. Please check the GitHub path.")
