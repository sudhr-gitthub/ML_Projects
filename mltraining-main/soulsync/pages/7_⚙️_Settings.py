import json
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.services.users import get_user, ensure_profile
from soulsync.services.export import export_user_json_bytes
from soulsync.services.account import delete_voice_history, delete_voice_memory, delete_account

load_css()


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)

    page_header("⚙️ Settings", "Privacy controls, data export, and delete tools")

    goals_data = {}
    if profile.goals_json:
        try:
            goals_data = json.loads(profile.goals_json)
        except Exception:
            goals_data = {}

    current_goals = goals_data.get("goals", [])
    current_note = goals_data.get("note", "")

    tz_options = ["Asia/Kolkata", "UTC", "Asia/Singapore", "Europe/London", "America/New_York"]
    tz_index = tz_options.index(profile.timezone) if profile.timezone in tz_options else 0

    with st.form("settings"):
        tz = st.selectbox("Timezone", tz_options, index=tz_index)

        goals = st.multiselect(
            "Goals",
            ["Study smarter", "Sleep better", "Eat healthier", "Move more", "Feel calmer", "Be kinder", "Be confident"],
            default=current_goals
        )
        note = st.text_input("Personal goal note", value=current_note)

        st.subheader("Privacy (opt-in)")
        consent_location = st.toggle("Location-based hidden missions", value=user.consent_location)
        consent_leaderboard = st.toggle("Leaderboards", value=user.consent_leaderboard)

        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City (optional)", value=user.city or "")
        with col2:
            region = st.text_input("Region/State (optional)", value=user.region or "")

        saved = st.form_submit_button("Save settings", type="primary")

    if saved:
        profile.timezone = tz
        profile.goals_json = json.dumps({"goals": goals, "note": note})
        user.consent_location = bool(consent_location)
        user.consent_leaderboard = bool(consent_leaderboard)
        user.city = city.strip() or None
        user.region = region.strip() or None
        db.commit()
        st.success("Saved!")

    st.markdown("---")
    st.markdown("## 📦 Export your data")
    st.caption("Download a minimal JSON file: profile, stats, missions, journal, and Your Voice memory. (No chat logs, no audit log.)")

    json_bytes = export_user_json_bytes(db, user.id)
    st.download_button(
        label="Download my data (JSON) ⬇️",
        data=json_bytes,
        file_name=f"soulsync_export_{user.handle}.json",
        mime="application/json",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("## 🧹 Delete controls")
    st.warning("These actions cannot be undone. Consider exporting your data first.")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### Delete chat history")
        st.caption("Removes messages in **Your Voice** chat (VoiceMessage).")
        if st.button("Delete my chat history 🗑️", type="secondary", use_container_width=True):
            n = delete_voice_history(db, user.id)
            db.commit()
            st.success(f"Deleted {n} chat message(s).")
            st.rerun()

    with colB:
        st.markdown("### Delete memory")
        st.caption("Removes **VoiceMemory** (journal mirrors, goals, summaries).")
        if st.button("Delete my memory 🧠🗑️", type="secondary", use_container_width=True):
            n = delete_voice_memory(db, user.id)
            db.commit()
            st.success(f"Deleted {n} memory item(s).")
            st.rerun()

    st.markdown("### Delete my account (full wipe)")
    st.caption("Deletes your profile, stats, missions, journal, voice data, leaderboard snapshots — everything.")

    confirm = st.text_input("Type your handle to confirm", placeholder=f"Type: {user.handle}")
    if st.button("DELETE ACCOUNT FOREVER ❗", type="primary", use_container_width=True):
        if confirm.strip() != user.handle:
            st.error("Handle did not match. Account not deleted.")
        else:
            delete_account(db, user.id)
            db.commit()
            st.session_state.clear()
            st.success("Your account was deleted. Goodbye 🌼")
            st.rerun()

    st.markdown("---")
    st.markdown("## Safety")
    st.info(
        "SoulSync is supportive, not medical advice. "
        "If you feel unsafe or might hurt yourself, contact local emergency services or a trusted adult."
    )

main()
