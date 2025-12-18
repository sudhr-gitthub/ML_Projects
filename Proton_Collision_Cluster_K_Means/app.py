import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import os

# --- Configuration ---
MODEL_FILE = 'kmeans_model.pkl'

def load_model():
    """Loads the KMeans model from the pickle file."""
    if not os.path.exists(MODEL_FILE):
        st.error(f"Error: Model file '{MODEL_FILE}' not found. Please upload it to the same directory as this script.")
        return None
    
    try:
        with open(MODEL_FILE, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def main():
    st.set_page_config(page_title="Proton Collision Clustering", page_icon="⚛️")

    st.title("⚛️ Proton Collision Cluster Prediction")
    st.markdown("""
    This app uses a **K-Means Clustering** model to classify proton collision data into distinct groups.
    Enter the two feature values below to see which cluster a specific collision event belongs to.
    """)

    # --- Load Model ---
    model = load_model()
    
    if model:
        # Check model metadata
        n_features = getattr(model, 'n_features_in_', 2)
        
        st.sidebar.header("Input Features")
        st.sidebar.info(f"Model expects {n_features} input features.")

        # --- Input Fields ---
        # Note: Since the exact feature names (e.g., 'Momentum X', 'Energy') aren't in the pkl, 
        # we use generic descriptive names. You can rename these if you know the specific physics metrics.
        feature_1 = st.sidebar.number_input("Feature 1 (e.g., x-coordinate / momentum)", value=0.0, format="%.4f")
        feature_2 = st.sidebar.number_input("Feature 2 (e.g., y-coordinate / energy)", value=0.0, format="%.4f")

        input_data = np.array([[feature_1, feature_2]])

        # --- Prediction ---
        if st.button("Predict Cluster"):
            try:
                # Predict the cluster
                cluster_label = model.predict(input_data)[0]
                st.success(f"The data point belongs to **Cluster {cluster_label}**")

                # --- Visualization ---
                st.subheader("Cluster Visualization")
                
                # Get cluster centers from the model
                centers = model.cluster_centers_
                
                # Create plot
                fig, ax = plt.subplots(figsize=(8, 5))
                
                # 1. Plot Cluster Centers
                ax.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.7, marker='*', label='Cluster Centers')
                
                # 2. Plot User Input
                ax.scatter(feature_1, feature_2, c='blue', s=150, edgecolors='black', label='Your Input')
                
                # Labels and Style
                for i, c in enumerate(centers):
                    ax.text(c[0], c[1], f" C{i}", fontsize=12, fontweight='bold')
                
                ax.set_xlabel("Feature 1")
                ax.set_ylabel("Feature 2")
                ax.set_title("Input Point vs. Cluster Centers")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.6)
                
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

if __name__ == "__main__":
    main()
