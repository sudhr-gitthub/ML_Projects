import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="ECG Heartbeat Classifier", page_icon="💓", layout="centered")

# --- 1. Load the Model ---
@st.cache_resource
def load_model():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'ecg_classifier.pkl')
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error(f"⚠️ Model file not found at: {model_path}")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# --- 2. UI Layout ---
st.title("💓 ECG Heartbeat Classifier")
st.markdown("Analyze ECG signals. **Note:** This model requires inputs of specific length (usually 187). Short inputs will be padded.")
st.divider()

# --- 3. Input Section ---
st.subheader("1. Input ECG Signal")
# Default example with exactly 187 zeros for safety, or a small sample
default_csv = "0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0" 
input_data = st.text_area("Paste CSV Data Here:", height=150, placeholder=default_csv)

# --- 4. Processing & Prediction ---
if st.button("Analyze Heartbeat", type="primary"):
    if not input_data:
        st.warning("Please enter some data first.")
    else:
        # --- STEP 1: PARSE INPUT ---
        try:
            # Clean and split data
            clean_str = input_data.replace('\n', ',')
            for char in ['[', ']', '(', ')']:
                clean_str = clean_str.replace(char, '')
            
            data_list = [float(x.strip()) for x in clean_str.split(',') if x.strip()]
        except ValueError:
            st.error("❌ Format Error: Could not read the numbers. Please remove any letters or text headers.")
            st.stop()

        # --- STEP 2: HANDLE DIMENSIONS ---
        if model:
            try:
                # Check what the model expects (usually 187 for MIT-BIH)
                if hasattr(model, 'n_features_in_'):
                    expected_features = model.n_features_in_
                else:
                    expected_features = 187 # Fallback standard

                current_features = len(data_list)
                
                # Auto-pad with zeros if too short
                if current_features < expected_features:
                    padding = [0.0] * (expected_features - current_features)
                    data_list.extend(padding)
                    st.warning(f"⚠️ Input had {current_features} points, but model expects {expected_features}. Padded with {len(padding)} zeros to prevent crash.")
                
                # Truncate if too long
                elif current_features > expected_features:
                    data_list = data_list[:expected_features]
                    st.warning(f"⚠️ Input was too long. Truncated to {expected_features} points.")

                # Create final array
                features = np.array(data_list).reshape(1, -1)

                # --- STEP 3: VISUALIZE ---
                st.subheader("2. Signal Visualization")
                # We show the padded signal so the user sees exactly what the model sees
                st.line_chart(pd.DataFrame(data_list, columns=["Amplitude"]))

                # --- STEP 4: PREDICT ---
                raw_prediction = model.predict(features)[0]
                
                # Interpret Result
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
                        
            except Exception as e:
                st.error(f"❌ Prediction Error: {e}")
