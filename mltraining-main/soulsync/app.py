import streamlit as st
from datetime import datetime

from soulsync.db import get_session, init_db
from soulsync.models import Base, User, Profile
from soulsync.security import valid_email, valid_handle
from soulsync.ui.styles import load_css, page_header

st.set_page_config(
    page_title="SoulSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
init_db(Base)

def ensure_user(email: str, handle: str) -> int:
    db = get_session()
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        user = User(email=email, handle=handle, consent_leaderboard=False, consent_location=False)
        db.add(user)
        db.flush()
        profile = Profile(user_id=user.id, timezone="UTC", streak_count=0, last_login_at=datetime.utcnow())
        db.add(profile)
        db.commit()
    else:
        if user.profile:
            user.profile.last_login_at = datetime.utcnow()
        db.commit()

    return user.id

def login_gate():
    page_header("✨ SoulSync", "A friendly life‑RPG for building real‑world habits.")
    st.markdown(
        "<div class='ss-card'>"
        "<b>Hi!</b> This is a demo login (no passwords yet). "
        "Use an email + a fun handle to start your journey."
        "<div class='ss-hr'></div>"
        "<span class='ss-muted'>Safety note: SoulSync gives supportive, non‑clinical tips. "
        "If you feel unsafe or need urgent help, contact local emergency services or a trusted adult.</span>"
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("login", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@example.com")
        handle = st.text_input("Handle (letters/numbers/_)", placeholder="SkyHero_21")
        submitted = st.form_submit_button("Start ✨", type="primary")

    if submitted:
        if not valid_email(email):
            st.error("Please enter a valid email.")
            return
        if not valid_handle(handle):
            st.error("Handle must be 3–32 characters, using letters/numbers/underscore.")
            return

        user_id = ensure_user(email.strip().lower(), handle.strip())
        st.session_state["user_id"] = user_id
        st.session_state["handle"] = handle.strip()
        st.success("Welcome! Opening your dashboard…")
        st.rerun()

def main():
    if "user_id" not in st.session_state:
        login_gate()
        return

    with st.sidebar:
        st.markdown("<div class='ss-card--panel'><b>Logged in as</b><br>"
                    f"@{st.session_state.get('handle','player')}</div>", unsafe_allow_html=True)
        st.caption("Use the pages in the left sidebar ✅")

    page_header("✨ SoulSync", "Use the sidebar pages to explore the modules as we build them.")
    st.markdown(
        "<div class='ss-card'>"
        "<b>Status:</b> Foundation module is running ✅<br>"
        "Next: onboarding consents, stat cards, daily missions."
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
