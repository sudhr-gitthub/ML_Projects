import streamlit as st
import joblib
import requests
import io

# --- Configuration ---
REPO_URL = "https://github.com/sudhr-gitthub/ML_Projects/raw/main/News_Headline_Clssifier_KNN"
MODEL_FILE = "News_headline_classifier.pkl"
# You MUST upload this file to your GitHub folder!
VECTORIZER_FILE = "news_vectorizer.pkl" 

# --- Functions ---
@st.cache_resource
def load_remote_file(filename):
    """Downloads a pickle file from GitHub and loads it."""
    url = f"{REPO_URL}/{filename}"
    try:
        with st.spinner(f"Downloading {filename}..."):
            response = requests.get(url)
            response.raise_for_status()
            return joblib.load(io.BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to load {filename}: {e}")
        return None

# --- Main App ---
def main():
    st.title("📰 News Headline Classifier")
    st.markdown(f"**Source:** [GitHub Repository]({REPO_URL})")

    # 1. Load Both Model and Vectorizer
    model = load_remote_file(MODEL_FILE)
    vectorizer = load_remote_file(VECTORIZER_FILE)

    # Check if both loaded successfully
    if model and vectorizer:
        st.success("System loaded successfully!")
        
        # 2. User Input
        user_input = st.text_area("Enter a News Headline:", height=100)

        # 3. Prediction
        if st.button("Classify"):
            if user_input.strip():
                try:
                    # TRANSFORM the text first
                    text_vector = vectorizer.transform([user_input])
                    
                    # PREDICT using the vector
                    prediction = model.predict(text_vector)
                    
                    st.subheader("Result:")
                    st.write(f"**Category:** {prediction[0]}")
                    
                except Exception as e:
                    st.error(f"Prediction Error: {e}")
            else:
                st.warning("Please enter a headline first.")
    
    elif not vectorizer:
        st.warning(f"⚠️ Could not find '{VECTORIZER_FILE}'. Please upload your vectorizer to GitHub.")

if __name__ == "__main__":
    main()
