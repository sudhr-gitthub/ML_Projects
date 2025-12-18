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
MODEL_PATH = 'mall_customer_hier.pkl'

# --- Load Model Function ---
@st.cache_resource
def load_model():
    """
    Loads the machine learning model safely.
    Checks if the file exists first.
    """
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        # Using joblib as it is standard for sklearn pickles
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

    if model is None:
        st.error(f"Could not find model file at: `{MODEL_PATH}`")
        st.warning("Please ensure the .pkl file is in the same directory as this app.py.")
        return

    # --- Sidebar ---
    st.sidebar.header("Model Status")
    st.sidebar.success("Model Loaded Successfully!")
    
    # --- Model Details Section ---
    st.subheader("📊 Model Configuration")
    
    # Extracting attributes from the AgglomerativeClustering object
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Algorithm", "Agglomerative Clustering")
        
    with col2:
        # n_clusters might be None if distance_threshold is used, handling that safely
        n_clusters = getattr(model, 'n_clusters_', 'N/A')
        st.metric("Clusters Found", n_clusters)
        
    with col3:
        linkage = getattr(model, 'linkage', 'ward')
        st.metric("Linkage Type", linkage.capitalize())

    st.divider()

    # --- Educational Logic: The "Predict" Constraint ---
    st.subheader("🤔 How to Predict New Customers?")
    
    st.info(
        """
        **Note on Hierarchical Clustering:** Unlike K-Means, `AgglomerativeClustering` does not natively support a `.predict()` method for new data points. 
        It is designed to group the *existing* data it was trained on.
        """
    )
    
    st.markdown("### Recommended Next Steps for Deployment")
    st.write("To enable a feature where you input 'Income' and 'Score' to get a Cluster ID, you can implement one of these approaches:")
    
    st.markdown("""
    1.  **Switch to K-Means:** If you re-train your model using `KMeans`, you can use `kmeans.predict([[income, score]])` directly.
    2.  **Train a Classifier:** You can use the `labels_` from this hierarchical model to train a `KNeighborsClassifier`. This classifier can then predict the cluster for new customers.
    """)

    # --- Cluster Distribution Visualization (if labels exist) ---
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
