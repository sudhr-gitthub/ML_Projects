import streamlit as st
import joblib
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Mall Customer Segmentation", page_icon="🛍️", layout="wide")

# --- Constants ---
current_dir = os.path.dirname(os.path.abspath(__file__))
CLUSTERING_MODEL_PATH = os.path.join(current_dir, 'mall_customer_hier.pkl')
PREDICTOR_MODEL_PATH = os.path.join(current_dir, 'mall_customer_predictor.pkl')
DATA_PATH = os.path.join(current_dir, 'Mall_Customers.csv')

# --- Load Functions ---
@st.cache_resource
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

@st.cache_resource
def load_clustering_model():
    if os.path.exists(CLUSTERING_MODEL_PATH):
        return joblib.load(CLUSTERING_MODEL_PATH)
    return None

@st.cache_resource
def load_predictor_model():
    if os.path.exists(PREDICTOR_MODEL_PATH):
        return joblib.load(PREDICTOR_MODEL_PATH)
    return None

def main():
    st.title("🛍️ Mall Customer Clustering Inspector")
    
    # Load Resources
    df = load_data()
    c_model = load_clustering_model()
    p_model = load_predictor_model()

    # --- Sidebar Status ---
    st.sidebar.header("System Status")
    if c_model:
        st.sidebar.success("✅ Clustering Model Loaded")
    else:
        st.sidebar.error("❌ Clustering Model Missing")
        
    if df is not None:
        st.sidebar.success("✅ Dataset Loaded")
    else:
        st.sidebar.warning("⚠️ Dataset Missing (Mall_Customers.csv)")

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "🔮 Predict Cluster", "📋 Data Overview"])

    # --- TAB 1: VISUALIZATIONS ---
    with tab1:
        if c_model and df is not None:
            # Prepare Data
            # Ensure we don't overwrite original df if re-running
            plot_df = df.copy()
            plot_df['Cluster'] = c_model.labels_
            plot_df['Cluster'] = plot_df['Cluster'].astype(str) # Convert to string for discrete colors
            
            # Layout Columns
            col_viz1, col_viz2 = st.columns([3, 1])
            
            with col_viz1:
                st.subheader("Interactive Cluster Map")
                # 2D Scatter Plot
                fig_2d = px.scatter(
                    plot_df,
                    x='Annual Income (k$)',
                    y='Spending Score (1-100)',
                    color='Cluster',
                    symbol='Cluster',
                    hover_data=['Age', 'Gender'],
                    title='Customer Segments: Income vs Spending',
                    template='plotly_white',
                    size_max=10
                )
                fig_2d.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                st.plotly_chart(fig_2d, use_container_width=True)

            with col_viz2:
                st.subheader("Distribution")
                # Donut Chart
                fig_pie = px.pie(
                    plot_df, 
                    names='Cluster', 
                    title='Size of Clusters', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_pie.update_layout(showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

            st.divider()

            # 3D Plot (Only if Age exists)
            if 'Age' in plot_df.columns:
                st.subheader("🧊 3D Perspective (Age, Income, Score)")
                fig_3d = px.scatter_3d(
                    plot_df,
                    x='Annual Income (k$)',
                    y='Spending Score (1-100)',
                    z='Age',
                    color='Cluster',
                    opacity=0.8,
                    title='3D Customer Segments'
                )
                st.plotly_chart(fig_3d, use_container_width=True)

        elif not df:
            st.error("Please upload 'Mall_Customers.csv' to the folder to see the visualizations.")
            st.info("The model stores labels, but we need the original Income/Score data to plot the dots!")

    # --- TAB 2: PREDICTION ---
    with tab2:
        st.header("Predict Customer Segment")
        if p_model:
            col1, col2 = st.columns(2)
            with col1:
                income = st.number_input("Annual Income (k$)", min_value=0, max_value=200, value=50)
            with col2:
                score = st.number_input("Spending Score (1-100)", min_value=1, max_value=100, value=50)
            
            if st.button("Predict Cluster", type="primary"):
                prediction = p_model.predict([[income, score]])
                cluster_id = prediction[0]
                st.success(f"This customer belongs to **Cluster {cluster_id}**")
        else:
            st.warning("To enable predictions, run 'build_predictor.py' locally first.")

    # --- TAB 3: DATA OVERVIEW ---
    with tab3:
        if df is not None:
            st.dataframe(df.head())
            st.caption("First 5 rows of the dataset")

if __name__ == "__main__":
    main()
