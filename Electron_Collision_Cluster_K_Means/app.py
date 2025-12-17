import streamlit as st
import joblib
import numpy as np
import requests
import io

# --- Page Config ---
st.set_page_config(page_title="Electron Collision Clustering", page_icon="⚛️")

# --- Function to Load Model from GitHub ---
@st.cache_resource
def load_model_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        
        # Load the model from the downloaded content
        # We use io.BytesIO to treat the byte content like a file
        model = joblib.load(io.BytesIO(response.content))
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# --- Main App ---
def main():
    st.title("⚛️ Electron Collision Cluster Predictor")
    st.write("This app uses a K-Means model loaded directly from GitHub to predict collision clusters.")

    # URL to the RAW file on GitHub
    # Format: https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path_to_file}
    github_url = "https://raw.githubusercontent.com/sudhr-gitthub/ML_Projects/main/Electron_Collision_Cluster_K_Means/kmeans_model.pkl"
    
    with st.spinner("Downloading model from GitHub..."):
        model = load_model_from_github(github_url)

    if model:
        st.success("Model loaded successfully!")
        
        # Display generic model info if available
        if hasattr(model, "n_features_in_"):
            st.info(f"The model expects **{model.n_features_in_}** input features.")
            expected_features = model.n_features_in_
        else:
            expected_features = None

        st.markdown("---")
        
        # --- Input Section ---
        st.subheader("Enter Collision Data")
        st.caption("Enter your data points separated by commas.")
        
        # Example placeholder tailored to expected physics data usually found in collision datasets
        input_str = st.text_input(
            "Input Features (e.g., Energy, Angle, etc.)", 
            placeholder="0.5, 12.3, 0.004..."
        )

        if st.button("Predict Cluster"):
            try:
                # Convert string input to numpy array
                input_list = [float(x.strip()) for x in input_str.split(',')]
                data_array = np.array(input_list).reshape(1, -1)

                # Validation: Check feature count if we know it
                if expected_features and data_array.shape[1] != expected_features:
                    st.error(f"❌ Input Error: You provided {data_array.shape[1]} features, but the model expects {expected_features}.")
                else:
                    # Prediction
                    prediction = model.predict(data_array)
                    
                    # Output
                    st.metric(label="Predicted Cluster ID", value=str(prediction[0]))
                    
                    # Optional: Show cluster centers if meaningful
                    if st.checkbox("Show Model Centroids"):
                        st.write(model.cluster_centers_)

            except ValueError:
                st.error("❌ Please enter valid numerical data separated by commas.")
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

if __name__ == "__main__":
    main()
