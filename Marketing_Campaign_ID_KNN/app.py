import streamlit as st
import pickle
import numpy as np
import requests
import io

# Set page configuration
st.set_page_config(page_title="Marketing Campaign Predictor", layout="centered")

st.title("Marketing Campaign Target Prediction")
st.write("Enter the customer's basic details below to predict the campaign response.")

# --- GitHub Model Connection ---
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
FILE_PATH = "Marketing_Campaign_ID_KNN/knn_model.pkl"
MODEL_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{FILE_PATH}"

@st.cache_resource
def load_model_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        model_file = io.BytesIO(response.content)
        model = pickle.load(model_file)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model_from_github(MODEL_URL)

if model:
    # --- Default Values for Hidden Features ---
    # These are the average values (means) from the training data.
    # We use these for the features we are not asking the user to input.
    defaults = {
        'MntWines': -0.00159,
        'MntFruits': -0.00752,
        'MntMeatProducts': 0.00719,
        'MntFishProducts': 0.00823,
        'MntSweetProducts': -0.00166,
        'MntGoldProds': 0.00289,
        'NumDealsPurchases': -0.00217,
        'NumWebPurchases': 0.02043,
        'NumCatalogPurchases': -0.01289,
        'NumStorePurchases': -0.01138,
        'NumWebVisitsMonth': 0.02621
    }

    # --- Simplified Input Form (Only 5 Inputs) ---
    st.subheader("Customer Details")
    
    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input("Income", value=50000.0, step=1000.0)
        age = st.number_input("Age", value=30, min_value=18, max_value=100, step=1)
        recency = st.number_input("Recency (Days)", value=50, min_value=0, step=1)

    with col2:
        kidhome = st.number_input("Kids at Home", value=0, min_value=0, step=1)
        teenhome = st.number_input("Teens at Home", value=0, min_value=0, step=1)

    # --- Prediction Logic ---
    if st.button("Predict Response"):
        # We construct the full input array expected by the model (16 features)
        # Order: Income, Age, Kidhome, Teenhome, Recency, MntWines, MntFruits, MntMeat, MntFish, MntSweet, MntGold, NumDeals, NumWeb, NumCatalog, NumStore, NumWebVisits
        
        # Note: The model appears to be trained on SCALED data (mean ~ 0).
        # Since we don't have the scaler file, we are passing raw inputs here.
        # ideally, you should apply the same scaler used during training.
        
        input_data = np.array([[
            income, 
            age, 
            kidhome, 
            teenhome, 
            recency,
            defaults['MntWines'],
            defaults['MntFruits'],
            defaults['MntMeatProducts'],
            defaults['MntFishProducts'],
            defaults['MntSweetProducts'],
            defaults['MntGoldProds'],
            defaults['NumDealsPurchases'],
            defaults['NumWebPurchases'],
            defaults['NumCatalogPurchases'],
            defaults['NumStorePurchases'],
            defaults['NumWebVisitsMonth']
        ]])
        
        try:
            prediction = model.predict(input_data)
            
            st.divider()
            if prediction[0] == 1:
                st.success("✅ Prediction: The customer is likely to ACCEPT the offer.")
            else:
                st.info("❌ Prediction: The customer is unlikely to accept the offer.")
                
        except Exception as e:
            st.error(f"Prediction Error: {e}")

else:
    st.warning("Could not load the model. Please check the repository settings.")
