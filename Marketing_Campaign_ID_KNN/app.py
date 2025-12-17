import streamlit as st
import pickle
import numpy as np
import requests
import io

# Set page configuration
st.set_page_config(page_title="Marketing Campaign Predictor", layout="centered")

st.title("Marketing Campaign Target Prediction")
st.write("This app connects to a KNN model hosted on GitHub to predict campaign response.")

# --- GitHub Model Connection ---
# Construct the raw URL for the file
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
FILE_PATH = "Marketing_Campaign_ID_KNN/knn_model.pkl"
MODEL_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{FILE_PATH}"

@st.cache_resource
def load_model_from_github(url):
    """Downloads and loads the pickle model from a GitHub raw URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        model_file = io.BytesIO(response.content)
        model = pickle.load(model_file)
        return model
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading model from GitHub: {e}")
        return None
    except Exception as e:
        st.error(f"Error loading pickle file: {e}")
        return None

# Load the model
model = load_model_from_github(MODEL_URL)

if model:
    st.success("Model loaded successfully from GitHub!")
    
    # --- Input Form ---
    st.subheader("Customer Details")
    
    # Using columns for a cleaner layout
    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input("Income", min_value=0.0, step=100.0, format="%.2f")
        age = st.number_input("Age", min_value=18, max_value=100, step=1)
        kidhome = st.number_input("Number of Kids at Home", min_value=0, step=1)
        teenhome = st.number_input("Number of Teens at Home", min_value=0, step=1)
        recency = st.number_input("Recency (Days since last purchase)", min_value=0, step=1)
        mnt_wines = st.number_input("Amount spent on Wines", min_value=0.0, step=1.0)
        mnt_fruits = st.number_input("Amount spent on Fruits", min_value=0.0, step=1.0)
        mnt_meat = st.number_input("Amount spent on Meat", min_value=0.0, step=1.0)

    with col2:
        mnt_fish = st.number_input("Amount spent on Fish", min_value=0.0, step=1.0)
        mnt_sweet = st.number_input("Amount spent on Sweets", min_value=0.0, step=1.0)
        mnt_gold = st.number_input("Amount spent on Gold", min_value=0.0, step=1.0)
        num_deals = st.number_input("Num Deals Purchases", min_value=0, step=1)
        num_web = st.number_input("Num Web Purchases", min_value=0, step=1)
        num_catalog = st.number_input("Num Catalog Purchases", min_value=0, step=1)
        num_store = st.number_input("Num Store Purchases", min_value=0, step=1)
        num_web_visits = st.number_input("Num Web Visits Month", min_value=0, step=1)

    # --- Prediction ---
    if st.button("Predict Response"):
        # Create input array based on the features expected by the model
        input_data = np.array([[
            income, age, kidhome, teenhome, recency, 
            mnt_wines, mnt_fruits, mnt_meat, mnt_fish, 
            mnt_sweet, mnt_gold, num_deals, num_web, 
            num_catalog, num_store, num_web_visits
        ]])
        
        try:
            prediction = model.predict(input_data)
            
            st.divider()
            st.subheader("Prediction Result")
            if prediction[0] == 1:
                st.success("The customer is likely to accept the campaign offer.")
            else:
                st.info("The customer is unlikely to accept the campaign offer.")
                
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")

else:
    st.warning("Please check the GitHub URL or repository status.")
