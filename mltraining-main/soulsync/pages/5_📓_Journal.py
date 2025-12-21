import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.journal import add_journal_entry
from soulsync.models import JournalEntry

load_css()

MOODS = ["great", "good", "okay", "low", "rough"]


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("📓 Journal", "A tiny reflection helps Your Voice support you better ✨")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    card(
        "<b>Tip:</b> Keep it simple — 3 lines is enough.<br>"
        "<span class='ss-muted'>Journal entries become private memory snippets for Your Voice (you can delete them).</span>",
        panel=True
    )

    with st.form("journal"):
        mood = st.selectbox("Mood", MOODS, index=2)
        text = st.text_area("What happened today?", placeholder="Example: I studied 20 mins, then got distracted…", height=120)
        tags = st.text_input("Tags (optional)", placeholder="study, friends, sleep")
        saved = st.form_submit_button("Save entry ✅", type="primary")

    if saved:
        if not text.strip():
            st.warning("Write at least one sentence ✍️")
        else:
            add_journal_entry(db, user.id, mood, text.strip(), tags.strip() or None)
            db.commit()
            st.success("Saved! Your Voice can now reference this 🧠✨")

    st.markdown("---")
    st.markdown("### Recent entries")
    rows = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).order_by(JournalEntry.created_at.desc()).limit(10).all()
    if not rows:
        st.info("No entries yet — try adding one above!")
    for r in rows:
        card(f"<b>{r.mood.upper()}</b> • <span class='ss-muted'>{r.created_at}</span><br>{r.text}")

main()
