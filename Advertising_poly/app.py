import streamlit as st
import pickle
import numpy as np

# -----------------------------
# Load the trained model
# -----------------------------
@st.cache_resource
def load_model():
    with open("advertising_poly_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Advertising Sales Prediction",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Advertising Sales Prediction (Polynomial Regression)")
st.write(
    """
    Predict **Sales** based on advertising spend in:
    - 📺 TV
    - 📻 Radio
    - 📰 Newspaper
    """
)

# -----------------------------
# User Inputs
# -----------------------------
tv = st.number_input("TV Advertising Spend", min_value=0.0, step=1.0)
radio = st.number_input("Radio Advertising Spend", min_value=0.0, step=1.0)
newspaper = st.number_input("Newspaper Advertising Spend", min_value=0.0, step=1.0)

# -----------------------------
# Prediction
# -----------------------------
if st.button("🔮 Predict Sales"):
    input_data = np.array([[tv, radio, newspaper]])

    try:
        prediction = model.predict(input_data)
        st.success(f"📊 Predicted Sales: **{prediction[0]:.2f}**")
    except Exception as e:
        st.error("⚠️ Prediction failed. Please check the model format.")
        st.exception(e)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Polynomial Regression Model • Streamlit App")
