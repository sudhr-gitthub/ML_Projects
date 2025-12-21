import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card, chip
from soulsync.constants import MISSION_EMOJI
from soulsync.services.users import get_user, ensure_profile, ensure_all_stats, is_onboarded
from soulsync.services.missions import get_todays_assignments, complete_assignment

load_css()

PROOF_TYPES = ["Quick note", "Photo URL", "Timer (minutes)"]

def proof_widget(key_prefix: str):
    ptype = st.selectbox("Proof (simple)", PROOF_TYPES, key=f"{key_prefix}_ptype")
    if ptype == "Quick note":
        note = st.text_input("Write a tiny note (optional)", key=f"{key_prefix}_note", placeholder="Example: Finished chapter 2!")
        return {"kind": "note", "value": note}
    if ptype == "Photo URL":
        url = st.text_input("Paste a photo URL (optional)", key=f"{key_prefix}_url", placeholder="https://...")
        return {"kind": "photo_url", "value": url}
    mins = st.number_input("Minutes", 1, 180, 20, key=f"{key_prefix}_mins")
    return {"kind": "timer_minutes", "value": int(mins)}

def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    ensure_all_stats(db, user.id)
    db.commit()

    if not is_onboarded(profile):
        page_header("✅ Missions", "Finish onboarding on the Dashboard first ✨")
        st.info("Go to **🏠 Dashboard** → complete the quick setup.")
        return

    page_header("✅ Missions", "Small steps. Big XP. You’ve got this 💪")

    day, rows = get_todays_assignments(db, user.id, profile.timezone)

    done = sum(1 for a, m in rows if a.status == "completed")
    total = len(rows)
    card(
        f"<b>Today:</b> {day.isoformat()}<br>"
        f"<b>Progress:</b> {done}/{total} completed<br>"
        f"<span class='ss-muted'>Tip: Completing all missions grows your streak and boosts XP bonuses.</span>",
        panel=True
    )

    st.markdown("### Your checklist")
    for a, m in rows:
        left, right = st.columns([0.72, 0.28], vertical_alignment="top")
        with left:
            emoji = MISSION_EMOJI.get(m.type, "✅")
            status = "✅ Completed" if a.status == "completed" else "⏳ Pending"
            chip(f"{emoji} <b>{m.type.title()}</b> • {m.difficulty.title()} • XP {m.xp_reward} • {status}")
            card(f"<b>{m.title}</b><br><span class='ss-muted'>Keep it simple — do your best.</span>")

        with right:
            if a.status == "completed":
                st.success("Done!")
            else:
                with st.expander("Complete + add proof"):
                    proof = proof_widget(f"proof_{a.id}")
                    if st.button("Mark complete ✅", key=f"complete_{a.id}", type="primary"):
                        res = complete_assignment(db, a.id, user.id, proof=proof)
                        db.commit()
                        if res.get("ok"):
                            st.toast(res["message"], icon="✨")
                            st.rerun()
                        else:
                            st.error(res.get("message", "Something went wrong."))

    st.markdown("---")
    st.caption("Accessibility: You can navigate with keyboard (Tab/Shift+Tab). Buttons have clear labels.")

main()
