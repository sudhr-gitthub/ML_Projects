import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
import pickle
import os

# Set page configuration
st.set_page_config(page_title="Mall Customer Segmentation", layout="wide")

def main():
    st.title("🛍️ Mall Customer Segmentation")
    st.markdown("### Hierarchical Clustering Model")
    
    # Sidebar for inputs
    st.sidebar.header("1. Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload Mall_Customers.csv", type=["csv"])
    
    st.sidebar.header("2. Model Configuration")
    # Default parameters based on typical Mall Customer models
    n_clusters = st.sidebar.slider("Number of Clusters", 2, 10, 5)
    linkage_method = st.sidebar.selectbox("Linkage Method", ["ward", "complete", "average", "single"])

    # Main interaction area
    if uploaded_file is not None:
        try:
            # Load dataset
            data = pd.read_csv(uploaded_file)
            st.write("### Data Preview")
            st.dataframe(data.head())

            # Data Preprocessing
            # Assuming standard columns: 'Annual Income (k$)' and 'Spending Score (1-100)'
            # Adjust column selection if your CSV headers differ
            if 'Annual Income (k$)' in data.columns and 'Spending Score (1-100)' in data.columns:
                X = data.iloc[:, [3, 4]].values
                feature_names = ['Annual Income (k$)', 'Spending Score (1-100)']
            else:
                st.warning("Standard columns not found. Using columns 3 and 4 by default.")
                X = data.iloc[:, [3, 4]].values
                feature_names = [data.columns[3], data.columns[4]]

            # ---------------------------------------------------------
            # VISUALIZATION 1: DENDROGRAM
            # ---------------------------------------------------------
            st.markdown("---")
            st.subheader("1. Dendrogram")
            st.write("The dendrogram helps determine the optimal number of clusters.")
            
            fig_dendro, ax_dendro = plt.subplots(figsize=(10, 5))
            #  - conceptual tag
            dendrogram = sch.dendrogram(sch.linkage(X, method=linkage_method), ax=ax_dendro)
            plt.title('Dendrogram')
            plt.xlabel('Customers')
            plt.ylabel('Euclidean Distances')
            st.pyplot(fig_dendro)

            # ---------------------------------------------------------
            # MODEL EXECUTION
            # ---------------------------------------------------------
            # Note: We re-instantiate the model here because AgglomerativeClustering 
            # cannot 'predict' on new data without re-fitting.
            hc = AgglomerativeClustering(n_clusters=n_clusters, metric='euclidean', linkage=linkage_method)
            y_hc = hc.fit_predict(X)
            
            # Add clusters to data
            data['Cluster'] = y_hc

            # ---------------------------------------------------------
            # VISUALIZATION 2: CLUSTER PLOT
            # ---------------------------------------------------------
            st.markdown("---")
            st.subheader("2. Cluster Visualization")
            
            fig_cluster, ax_cluster = plt.subplots(figsize=(10, 6))
            
            # Create a dynamic scatter plot based on the number of clusters
            for i in range(n_clusters):
                plt.scatter(X[y_hc == i, 0], X[y_hc == i, 1], s=100, label=f'Cluster {i+1}')

            plt.title('Clusters of Customers')
            plt.xlabel(feature_names[0])
            plt.ylabel(feature_names[1])
            plt.legend()
            st.pyplot(fig_cluster)
            
            # Show clustered data
            st.markdown("### Clustered Data Details")
            st.dataframe(data)
            
            # Option to save results
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Clustered Data as CSV",
                data=csv,
                file_name='mall_customers_segmented.csv',
                mime='text/csv',
            )

        except Exception as e:
            st.error(f"Error processing data: {e}")
            
    else:
        st.info("Awaiting CSV file upload. Please upload `Mall_Customers.csv` to proceed.")
        
        # Section for loading the specific pickle if strictly needed for inspection
        if os.path.exists("mall_customer_hier.pkl"):
            st.markdown("---")
            st.markdown("**Model Artifact Status:** `mall_customer_hier.pkl` detected.")
            if st.button("Load Pickle Parameters"):
                try:
                    with open("mall_customer_hier.pkl", "rb") as f:
                        loaded_model = pickle.load(f)
                    st.json({
                        "Model Type": type(loaded_model).__name__,
                        "Params": loaded_model.get_params(),
                        "N Clusters": loaded_model.n_clusters
                    })
                    st.caption("Note: This model does not support direct prediction on new data without refitting.")
                except Exception as e:
                    st.error(f"Could not read pickle file: {e}")

if __name__ == '__main__':
    main()
