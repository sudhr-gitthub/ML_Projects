import streamlit as st
import joblib
import os
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Mall Customer Segmentation",
    page_icon="🛍️",
    layout="wide"
)

# --- Constants ---
# FIX: Get the absolute path of the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the model file
MODEL_PATH = os.path.join(current_dir, 'mall_customer_hier.pkl')

# --- Load Model Function ---
@st.cache_resource
def load_model():
    """
    Loads the machine learning model safely using absolute paths.
    """
    if not os.path.exists(MODEL_PATH):
        # Return None and let the main function handle the error display
        return None
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# --- Main Application Logic ---
def main():
    st.title("🛍️ Mall Customer Clustering Inspector")
    st.write("View the details of the Hierarchical Clustering model used for customer segmentation.")

    # Load the model
    model = load_model()

    # Check if model loaded successfully
    if model is None:
        st.error(f"Could not find model file at: `{MODEL_PATH}`")
        st.warning(f"Script location: `{current_dir}`")
        st.info("Please ensure 'mall_customer_hier.pkl' is inside the 'Mall_Customer' folder alongside 'app.py'.")
        return

    # --- Sidebar ---
    st.sidebar.header("Model Status")
    st.sidebar.success("Model Loaded Successfully!")
    
    # --- Model Details Section ---
    st.subheader("📊 Model Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Algorithm", "Agglomerative Clustering")
        
    with col2:
        # Safely access attributes (some might be None depending on training parameters)
        n_clusters = getattr(model, 'n_clusters_', 'N/A')
        st.metric("Clusters Found", n_clusters)
        
    with col3:
        linkage = getattr(model, 'linkage', 'ward')
        st.metric("Linkage Type", linkage.capitalize())

    st.divider()

    # --- Educational Logic ---
    st.subheader("🤔 How to Predict New Customers?")
    
    st.info(
        """
        **Note on Hierarchical Clustering:** This specific algorithm (`AgglomerativeClustering`) groups 
        the data provided during training but does not have a standard `.predict()` function for new customers.
        """
    )
    
    st.markdown("### Recommended Next Steps for Deployment")
    st.markdown("""
    To enable a live prediction feature (e.g., inputting Income/Score to get a Cluster ID):
    1.  **Train a Classifier:** Extract the cluster labels from this model and train a **K-Nearest Neighbors (KNN)** or **Random Forest** classifier on them.
    2.  **Use the Classifier:** Save that classifier and use it here to predict new inputs.
    """)

    # --- Cluster Distribution Visualization ---
    if hasattr(model, 'labels_'):
        st.subheader("📉 Saved Training Data Distribution")
        st.write("Below is the distribution of customers across clusters from the saved model state:")
        
        labels = model.labels_
        unique, counts = np.unique(labels, return_counts=True)
        df_counts = pd.DataFrame({'Cluster ID': unique, 'Customer Count': counts})
        
        st.bar_chart(df_counts.set_index('Cluster ID'))
        
        with st.expander("View Raw Cluster Labels"):
            st.write(labels)

if __name__ == "__main__":
    main()
