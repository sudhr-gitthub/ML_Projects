import time
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import bubble, card
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.voice import chat_once, get_conversation, list_memory, delete_memory_item, MAX_MSG_PER_5MIN
from soulsync.services.moderation import CRISIS_RESOURCES_TEXT

load_css()


def _rate_limit_ok():
    now = time.time()
    history = st.session_state.get("voice_msg_times", [])
    history = [t for t in history if now - t < 300]
    st.session_state["voice_msg_times"] = history
    if len(history) >= MAX_MSG_PER_5MIN:
        return False, 300 - (now - history[0])
    history.append(now)
    st.session_state["voice_msg_times"] = history
    return True, 0


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("💬 Your Voice", "A supportive, non‑clinical buddy that learns from your journal + missions.")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    card(
        "<b>Hi! I’m Your Voice 🐣</b><br>"
        "Tell me how your day is going, or ask for a tiny next step.<br>"
        "<span class='ss-muted'>I’m supportive, not a therapist. If you feel unsafe, reach out to a trusted adult or emergency services.</span>",
        panel=True
    )

    with st.expander("🧩 Safety & help resources", expanded=False):
        st.write(CRISIS_RESOURCES_TEXT)

    st.markdown("### Chat")
    convo = get_conversation(db, user.id, limit=50)
    st.markdown("<div class='ss-bubble-wrap'>", unsafe_allow_html=True)
    for msg in convo:
        bubble(msg.role, msg.text)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Send a message")
    user_text = st.text_area("Type here (keep it kind 💛)", placeholder="Example: I kept procrastinating today…", height=90)

    col1, col2 = st.columns([0.75, 0.25])
    with col1:
        send = st.button("Send ✨", type="primary")
    with col2:
        clear = st.button("Clear input")

    if clear:
        st.rerun()

    if send:
        ok, wait_s = _rate_limit_ok()
        if not ok:
            st.warning(f"Slow down a bit 🌼 Try again in ~{int(wait_s)} seconds.")
        elif not user_text.strip():
            st.info("Type something first ✍️")
        else:
            _ = chat_once(db, user.id, user_text.strip())
            db.commit()
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Memory (what I can reference)")
    st.caption("This is stored in your database. You can delete items any time.")

    mems = list_memory(db, user.id, limit=30)
    if not mems:
        st.info("No memory yet. Add a journal entry 📓 to build helpful context!")
    else:
        for m in mems:
            card(
                f"<b>#{m.id}</b> <span class='ss-badge'>{m.kind}</span><br>"
                f"{m.content}<br><span class='ss-muted'>{m.created_at}</span>"
            )
            if st.button(f"Delete memory #{m.id}", key=f"delmem_{m.id}"):
                delete_memory_item(db, user.id, m.id)
                db.commit()
                st.toast("Deleted ✅", icon="🗑️")
                st.rerun()

main()
