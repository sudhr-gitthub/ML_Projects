import streamlit as st
import joblib
import os
import pandas as pd
import numpy as np
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Mall Customer Segmentation", page_icon="🛍️", layout="wide")

# --- Constants ---
current_dir = os.path.dirname(os.path.abspath(__file__))
CLUSTERING_MODEL_PATH = os.path.join(current_dir, 'mall_customer_hier.pkl')
PREDICTOR_MODEL_PATH = os.path.join(current_dir, 'mall_customer_predictor.pkl')
DATA_PATH = os.path.join(current_dir, 'Mall_Customers.csv')

# --- Helper: Robust Column Finder ---
def get_column_by_keyword(df, keyword):
    """Finds a column that contains the keyword (case-insensitive)."""
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    return None

# --- Load Functions ---
@st.cache_resource
def load_data():
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            # --- Robust Renaming ---
            # Try to standardize column names if they are slightly different
            rename_map = {}
            
            inc_col = get_column_by_keyword(df, 'income')
            if inc_col: rename_map[inc_col] = 'Annual Income (k$)'
            
            score_col = get_column_by_keyword(df, 'score')
            if score_col: rename_map[score_col] = 'Spending Score (1-100)'
            
            if rename_map:
                df = df.rename(columns=rename_map)
            
            return df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return None
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
            # Check required columns
            required_cols = ['Annual Income (k$)', 'Spending Score (1-100)']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing columns in CSV: {missing_cols}")
                st.write("Available columns:", df.columns.tolist())
            else:
                # Prepare Data
                plot_df = df.copy()
                plot_df['Cluster'] = c_model.labels_
                plot_df['Cluster'] = plot_df['Cluster'].astype(str)
                
                # Dynamic Hover Data (Only use columns that actually exist)
                hover_cols = [c for c in ['Age', 'Gender', 'CustomerID'] if c in plot_df.columns]

                # Layout Columns
                col_viz1, col_viz2 = st.columns([3, 1])
                
                with col_viz1:
                    st.subheader("Interactive Cluster Map")
                    try:
                        fig_2d = px.scatter(
                            plot_df,
                            x='Annual Income (k$)',
                            y='Spending Score (1-100)',
                            color='Cluster',
                            symbol='Cluster',
                            hover_data=hover_cols, # <--- Safe dynamic list
                            title='Customer Segments: Income vs Spending',
                            template='plotly_white',
                            size_max=10
                        )
                        fig_2d.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                        st.plotly_chart(fig_2d, use_container_width=True)
                    except Exception as e:
                        st.error(f"Plotting Error: {e}")

                with col_viz2:
                    st.subheader("Distribution")
                    fig_pie = px.pie(
                        plot_df, 
                        names='Cluster', 
                        title='Size of Clusters', 
                        hole=0.4
                    )
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.divider()

                # 3D Plot (Safe Check)
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
            st.error("Please upload 'Mall_Customers.csv' to the folder.")

    # --- TAB 2: PREDICTION ---
    with tab2:
        st.header("Predict Customer Segment")
        if p_model:
            col1, col2 = st.columns(2)
            with col1:
                income = st.number_input("Annual Income (k$)", 0, 200, 50)
            with col2:
                score = st.number_input("Spending Score (1-100)", 1, 100, 50)
            
            if st.button("Predict Cluster", type="primary"):
                try:
                    prediction = p_model.predict([[income, score]])
                    st.success(f"Cluster: **{prediction[0]}**")
                except Exception as e:
                    st.error(f"Prediction Error: {e}")
        else:
            st.warning("Predictor model missing. Run 'build_predictor.py'.")

    # --- TAB 3: DATA OVERVIEW ---
    with tab3:
        if df is not None:
            st.write("Data Columns Detected:", df.columns.tolist())
            st.dataframe(df.head())

if __name__ == "__main__":
    main()
