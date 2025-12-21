import json
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card
from soulsync.constants import STAT_LABELS, STAT_EMOJI, XP_BASE, MAX_LEVEL
from soulsync.services.users import get_user, ensure_profile, ensure_all_stats, is_onboarded
from soulsync.services.missions import get_todays_assignments
from soulsync.services.stats import xp_needed_for_level
from soulsync.models import Stat

load_css()

def onboarding_panel(db, user, profile):
    page_header("🏠 Dashboard", "Let’s set up your SoulSync journey ✨")

    st.markdown(
        "<div class='ss-card'>"
        "<b>Hi, I’m your cheerful guide!</b> 🧚‍♀️ "
        "I’ll help you build small habits that level up your stats.<br>"
        "<div class='ss-hr'></div>"
        "<span class='ss-muted'>Privacy: Location and leaderboards are <b>optional</b>. "
        "You can change these any time in Settings.</span>"
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("onboarding"):
        goals = st.multiselect(
            "Pick a few goals (you can change these later)",
            ["Study smarter", "Sleep better", "Eat healthier", "Move more", "Feel calmer", "Be kinder", "Be confident"],
            default=["Study smarter", "Sleep better"]
        )
        goal_note = st.text_input("One personal goal (optional)", placeholder="Example: Finish homework before 8 PM")

        tz = st.selectbox(
            "Your timezone",
            ["Asia/Kolkata", "UTC", "Asia/Singapore", "Europe/London", "America/New_York"],
            index=0
        )

        st.subheader("Optional consents")
        consent_location = st.toggle("Enable location-based hidden missions (opt-in)", value=user.consent_location)
        consent_leaderboard = st.toggle("Join leaderboards (opt-in, pseudonyms only)", value=user.consent_leaderboard)

        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City (optional)", value=user.city or "")
        with col2:
            region = st.text_input("Region/State (optional)", value=user.region or "")

        st.caption("Safety note: SoulSync gives supportive, non‑clinical guidance. If you feel unsafe, reach out to a trusted adult or local emergency services.")
        submitted = st.form_submit_button("Save & Start ✨", type="primary")

    if submitted:
        profile.timezone = tz
        profile.goals_json = json.dumps({"goals": goals, "note": goal_note})
        user.consent_location = bool(consent_location)
        user.consent_leaderboard = bool(consent_leaderboard)
        user.city = city.strip() or None
        user.region = region.strip() or None
        db.commit()
        st.success("All set! Loading your dashboard…")
        st.rerun()

def stat_cards(db, user_id: int):
    stats = {s.type: s for s in db.query(Stat).filter(Stat.user_id == user_id).all()}

    st.markdown("<div class='ss-row'>", unsafe_allow_html=True)
    for t in STAT_LABELS.keys():
        s = stats.get(t)
        if not s:
            continue
        next_need = 0 if s.level >= MAX_LEVEL else xp_needed_for_level(s.level, base=XP_BASE)
        pct = 1.0 if next_need == 0 else min(1.0, (s.xp / next_need) if next_need else 0)

        html = (
            f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
            f"<div><div style='font-size:1.05rem; font-weight:800;'>{STAT_EMOJI[t]} {STAT_LABELS[t]}</div>"
            f"<div class='ss-muted'>Level <b>{s.level}</b> / {MAX_LEVEL}</div></div>"
            f"<div class='ss-badge'>XP {s.xp}/{next_need if next_need else 'MAX'}</div>"
            f"</div>"
        )
        st.markdown("<div class='ss-col-4'>", unsafe_allow_html=True)
        card(html)
        st.progress(pct)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def todays_snapshot(db, user, profile):
    day, rows = get_todays_assignments(db, user.id, profile.timezone)
    done = sum(1 for a, m in rows if a.status == "completed")
    total = len(rows)

    st.markdown("<div class='ss-row'>", unsafe_allow_html=True)

    st.markdown("<div class='ss-col-6'>", unsafe_allow_html=True)
    card(
        f"<b>🔥 Streak</b><br>"
        f"<span style='font-size:2rem; font-weight:900;'>{profile.streak_count}</span> day(s)<br>"
        f"<span class='ss-muted'>Complete all daily missions to grow your streak.</span>",
        panel=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-col-6'>", unsafe_allow_html=True)
    card(
        f"<b>✅ Today’s Missions</b><br>"
        f"<span style='font-size:2rem; font-weight:900;'>{done}/{total}</span> completed<br>"
        f"<span class='ss-muted'>Date: {day.isoformat()} (timezone: {profile.timezone})</span>",
        panel=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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
        onboarding_panel(db, user, profile)
        return

    page_header("🏠 Dashboard", "Your stats level up when you complete missions ✨")
    todays_snapshot(db, user, profile)

    st.markdown("### 🌈 Your Stats")
    stat_cards(db, user.id)

    st.info("Next: go to **✅ Missions** to complete today’s checklist!")

main()
