from pathlib import Path
import streamlit as st

def load_css():
    css_path = Path("assets/theme.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

def page_header(title: str, subtitle: str | None = None):
    st.markdown(f"<h1 class='ss-title'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='ss-subtitle ss-muted'>{subtitle}</div>", unsafe_allow_html=True)
