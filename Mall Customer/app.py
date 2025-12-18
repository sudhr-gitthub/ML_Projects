import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import dendrogram, linkage
import joblib

st.set_page_config(layout="wide")

st.title("Mall Customer Segmentation - Hierarchical Clustering")

# Load the preprocessed data
@st.cache_data
def load_data():
    try:
        df = joblib.load('mall_customers.pkl')
        return df
    except FileNotFoundError:
        st.error("Error: 'mall_customers.pkl' not found. Please ensure the file is generated in the Colab environment.")
        return None

df = load_data()

if df is not None:
    st.subheader("Original DataFrame Head (Preprocessed)")
    st.dataframe(df.head())

    # Scale the features (re-apply scaling as `X_scaled` was not saved)
    st.subheader("Scaling Features for Clustering")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    st.write("Features scaled using StandardScaler.")

    # Perform hierarchical clustering
    st.subheader("Hierarchical Clustering Dendrogram")
    linked = linkage(X_scaled, method="ward")

    fig, ax = plt.subplots(figsize=(12, 7))
    dendrogram(linked, ax=ax)
    ax.set_title("Dendrogram for Hierarchical Clustering")
    ax.set_xlabel("Customers")
    ax.set_ylabel("Euclidean Distance")
    st.pyplot(fig)

    st.markdown("--- Developed with Streamlit --- ")
else:
    st.write("Please ensure the data preprocessing and saving steps were completed successfully in Colab.")
