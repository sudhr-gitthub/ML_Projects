import streamlit as st
import pandas as pd
import requests
import io

# --- 1. Page Configuration (Must be the first command) ---
st.set_page_config(
    page_title="Market Basket Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS for UI Polish ---
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GitHub Connection Logic (UNCHANGED) ---
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
FILE_PATH = "Groceries_Billing/groceries_billing.pkl"
URL = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{BRANCH}/{FILE_PATH}?raw=true"

@st.cache_data(show_spinner=False)
def load_model_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = pd.read_pickle(io.BytesIO(response.content))
        return data
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return pd.DataFrame()

# --- 4. Main App Interface ---
def main():
    # Header Section
    col_header, col_logo = st.columns([5, 1])
    with col_header:
        st.title("🛒 Groceries Billing Analysis")
        st.markdown(f"**Live Connection:** `{GITHUB_USER}/{REPO_NAME}`")
    with col_logo:
        # Just a placeholder for a logo or status indicator
        st.success("System Online")

    # Load Data with a clean toast notification instead of a huge spinner
    with st.spinner('Fetching data from GitHub...'):
        df = load_model_from_github(URL)
        # Optional: Normalize column names if needed
        # df.columns = [c.capitalize() for c in df.columns] 

    if not df.empty:
        # --- Sidebar UI ---
        with st.sidebar:
            st.header("⚙️ Configuration")
            st.write("Refine your analysis parameters below.")
            st.divider()

            # Input 1: Search
            st.subheader("🔍 Search Item")
            search_term = st.text_input("Filter by Product", placeholder="e.g., milk, yogurt")

            # Input 2: Slider
            st.subheader("📊 Support Threshold")
            if 'Support' in df.columns:
                min_val = float(df['Support'].min())
                max_val = float(df['Support'].max())
                selected_support = st.slider(
                    "Minimum Support",
                    min_value=min_val,
                    max_value=max_val,
                    value=min_val,
                    format="%.4f"
                )
            else:
                selected_support = 0.0
            
            st.divider()
            st.caption("Data source: GitHub Repository")

        # --- Logic (Filtering) ---
        df_filtered = df.copy()
        
        # Apply Support Filter
        if 'Support' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Support'] >= selected_support]
        
        # Apply Search Filter
        if search_term and 'Itemset' in df_filtered.columns:
            df_filtered = df_filtered[
                df_filtered['Itemset'].astype(str).str.contains(search_term, case=False)
            ]

        # --- Main Dashboard Area ---
        
        # Top Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Associations", len(df))
        m2.metric("Filtered Rules", len(df_filtered), delta=f"{len(df_filtered)-len(df)}")
        m3.metric("Min Support Found", f"{df_filtered['Support'].min():.4f}" if not df_filtered.empty else "0")

        st.markdown("---")

        # --- Tabs for Better Organization ---
        tab1, tab2 = st.tabs(["📄 Detailed Data", "📈 Visual Insights"])

        with tab1:
            st.subheader("Association Rules Table")
            
            # IMPROVED UI: Use column configuration to make the table look professional
            st.dataframe(
                df_filtered.sort_values(by='Support', ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Itemset": st.column_config.TextColumn(
                        "Product Combination",
                        help="Items bought together",
                        width="large"
                    ),
                    "Support": st.column_config.ProgressColumn(
                        "Support Score",
                        help="Frequency of occurrence",
                        format="%.4f",
                        min_value=0,
                        max_value=1,  # Assuming support is 0-1
                    ),
                    "Size": st.column_config.NumberColumn(
                        "Item Count",
                        format="%d items"
                    )
                }
            )

        with tab2:
            st.subheader("Top Performing Itemsets")
            if not df_filtered.empty and 'Support' in df_filtered.columns:
                top_15 = df_filtered.nlargest(15, 'Support')
                
                # Using a native bar chart, but horizontal for better readability of names
                st.bar_chart(
                    top_15.set_index('Itemset')['Support'],
                    color="#FF4B4B", # Streamlit Red
                    height=400
                )
            else:
                st.info("No data available to visualize with current filters.")

    else:
        st.error("Could not retrieve data. Please check the GitHub path or repository privacy settings.")

if __name__ == "__main__":
    main()
