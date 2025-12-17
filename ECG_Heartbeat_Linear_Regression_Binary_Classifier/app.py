import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os

# Page Configuration
st.set_page_config(
    page_title="ECG Heartbeat Classifier",
    page_icon="💓",
    layout="centered"
)

# --- 1. Load the Model (FIXED PATHING) ---
@st.cache_resource
def load_model():
    try:
        # Get the absolute path of the directory where this app.py file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the full path to the pickle file
        model_path = os.path.join(current_dir, 'ecg_classifier.pkl')
        
        # Load the model
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error(f"⚠️ Model file not found at: {model_path}")
        st.warning("Please ensure 'ecg_classifier.pkl' is committed to the same folder as 'app.py' in your GitHub repository.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- 2. UI Layout ---
st.title("💓 ECG Heartbeat Classifier")
st.markdown("""
This app analyzes ECG heartbeat signals to detect anomalies.
* **Model Type:** Linear Regression (acting as Binary Classifier)
* **Input:** Raw ECG signal data (comma-separated values)
""")

st.divider()

# --- 3. Input Section ---
st.subheader("1. Input ECG Signal")
st.caption("Paste your signal data below (e.g., 0.9, 0.5, 0.1, ...). Standard ECG samples usually have 187 or more points.")

default_csv = "0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0" 
input_data = st.text_area("Paste CSV Data Here:", height=150, placeholder=default_csv)

# --- 4. Processing & Prediction ---
if st.button("Analyze Heartbeat", type="primary"):
    if not input_data:
        st.warning("Please enter some data first.")
    else:
        try:
            # Convert string input to list of floats
            clean_input = input_data.replace('\n', ',')
            data_list = [float(x.strip()) for x in clean_input.split(',') if x.strip()]
            
            # Convert to numpy array
            features = np.array(data_list).reshape(1, -1)
            
            # --- Visualization ---
            st.subheader("2. Signal Visualization")
            chart_data = pd.DataFrame(data_list, columns=["Amplitude"])
            st.line_chart(chart_data)

            if model:
                # Prediction
                raw_prediction = model.predict(features)[0]
                
                # --- Interpretation ---
                st.subheader("3. Result")
                threshold = 0.5 
                result_class = 1 if raw_prediction > threshold else 0
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Raw Score", f"{raw_prediction:.4f}")
                
                with col2:
                    if result_class == 1:
                        st.error("Prediction: Abnormal (1)")
                    else:
                        st.success("Prediction: Normal (0)")
                        
                st.info(f"Note: This model uses a threshold of {threshold}. Scores above this are classified as Abnormal.")

        except ValueError:
            st.error("❌ Format Error: Please ensure the input contains only numbers separated by commas.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Sidebar
st.sidebar.header("About")
st.sidebar.info("This application is deployed from the GitHub repository: ML_Projects/ECG_Heartbeat_Linear_Regression_Binary_Classifier")
