import streamlit as st

def card(html_inside: str, panel: bool = False):
    klass = "ss-card--panel" if panel else "ss-card"
    st.markdown(f"<div class='{klass}'>{html_inside}</div>", unsafe_allow_html=True)

def chip(text: str):
    st.markdown(f"<span class='ss-chip'>{text}</span>", unsafe_allow_html=True)

def bubble(role: str, text: str):
    role_class = "user" if role == "user" else "assistant"
    st.markdown(f"<div class='ss-bubble {role_class}'>{text}</div>", unsafe_allow_html=True)
