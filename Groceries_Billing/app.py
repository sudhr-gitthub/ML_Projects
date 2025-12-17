import streamlit as st
import pandas as pd
import requests
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Groceries Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

# --- GitHub URL Construction ---
# We append '?raw=true' to ensure we get the binary file, not the GitHub HTML page.
GITHUB_USER = "sudhr-gitthub"
REPO_NAME = "ML_Projects"
BRANCH = "main"
FILE_PATH = "Groceries_Billing/groceries_billing.pkl"

URL = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{BRANCH}/{FILE_PATH}?raw=true"

# --- Data Loading Function ---
@st.cache_data
def load_model_from_github(url):
    """
    Fetches a pickled pandas DataFrame from a GitHub raw URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        # Load the content into a bytes buffer and read with pandas
        data = pd.read_pickle(io.BytesIO(response.content))
        return data
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return pd.DataFrame()

# --- Main App Interface ---
def main():
    st.title("🛒 Groceries Billing: Market Basket Analysis")
    st.markdown(f"**Data Source:** Connected to `{GITHUB_USER}/{REPO_NAME}`")

    with st.spinner('Downloading model data from GitHub...'):
        df = load_model_from_github(URL)

    if not df.empty:
        # Sidebar for Filtering
        st.sidebar.header("Filter Options")
        
        # 1. Filter by Minimum Support
        if 'Support' in df.columns:
            min_support = df['Support'].min()
            max_support = df['Support'].max()
            selected_support = st.sidebar.slider(
                "Minimum Support Threshold",
                min_value=float(min_support),
                max_value=float(max_support),
                value=float(min_support),
                format="%.4f"
            )
            df_filtered = df[df['Support'] >= selected_support]
        else:
            df_filtered = df

        # 2. Filter by Item Name (Search)
        if 'Itemset' in df.columns:
            search_term = st.sidebar.text_input("Search for an item (e.g., 'milk')")
            if search_term:
                # Filter rows where the itemset contains the search term (case-insensitive)
                df_filtered = df_filtered[
                    df_filtered['Itemset'].astype(str).str.contains(search_term, case=False)
                ]

        # --- Display Metrics ---
        col1, col2 = st.columns(2)
        col1.metric("Total Rules/Itemsets", len(df))
        col2.metric("Filtered Results", len(df_filtered))

        # --- Display Data ---
        st.subheader("Association Rules Data")
        st.dataframe(
            df_filtered.sort_values(by='Support', ascending=False),
            use_container_width=True
        )

        # --- Simple Visualization ---
        if not df_filtered.empty and 'Support' in df_filtered.columns:
            st.subheader("Top 10 Itemsets by Support")
            top_10 = df_filtered.nlargest(10, 'Support')
            st.bar_chart(top_10.set_index('Itemset')['Support'])

    else:
        st.warning("No data found or failed to load the pickle file.")

if __name__ == "__main__":
    main()
