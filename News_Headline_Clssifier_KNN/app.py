import streamlit as st
import joblib
import requests
import io
import numpy as np

# --- Configuration ---
# The raw URL to your GitHub file. 
# Note: We use raw.githubusercontent.com to get the actual file content.
GITHUB_MODEL_URL = "https://github.com/sudhr-gitthub/ML_Projects/raw/main/News_Headline_Clssifier_KNN/News_headline_classifier.pkl"

# --- Functions ---

@st.cache_resource
def load_model_from_github(url):
    """
    Downloads the model file from GitHub and loads it into memory.
    Using @st.cache_resource ensures we only download it once.
    """
    try:
        with st.spinner(f"Downloading model from GitHub..."):
            response = requests.get(url)
            response.raise_for_status()  # Check for errors (e.g., 404 Not Found)
            
            # Load the model from the bytes downloaded
            model = joblib.load(io.BytesIO(response.content))
            return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# --- Main App ---

def main():
    st.title("📰 News Headline Classifier")
    st.markdown(f"**Model Source:** [GitHub Repository]({GITHUB_MODEL_URL})")

    # 1. Load the Model
    model = load_model_from_github(GITHUB_MODEL_URL)

    if model:
        st.success("Model loaded successfully!")
        
        # 2. User Input
        user_input = st.text_area("Enter a News Headline:", height=100)

        # 3. Prediction
        if st.button("Classify"):
            if user_input.strip():
                try:
                    # NOTE: A KNN model typically requires numeric input (vectors).
                    # If your .pkl file contains ONLY the classifier (and not a full Pipeline with a vectorizer),
                    # you must vectorizer the text here exactly as you did in training.
                    # 
                    # Assuming the model might handle text or you have a vectorizer loaded:
                    prediction = model.predict([user_input])
                    
                    st.subheader("Result:")
                    st.write(f"**Category:** {prediction[0]}")
                    
                except ValueError as e:
                    st.error("Error during prediction. The model expects numeric features (vectors) but received text.")
                    st.info("Tip: If you trained with a TfidfVectorizer or CountVectorizer, you must also save/load that vectorizer and transform the input text before passing it to this model.")
                    st.code("vectorized_text = vectorizer.transform([user_input])\nprediction = model.predict(vectorized_text)")
            else:
                st.warning("Please enter a headline first.")

if __name__ == "__main__":
    main()
