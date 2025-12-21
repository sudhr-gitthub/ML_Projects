import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.leaderboard import recalc_leaderboard

load_css()


def rank_badge(rank: int) -> str:
    if rank == 1:
        return "🥇 Champion"
    if rank == 2:
        return "🥈 Runner-up"
    if rank == 3:
        return "🥉 Top 3"
    if rank <= 10:
        return "🌟 Top 10"
    return "✨"


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("🏆 Leaderboard", "Opt‑in only. Gentle competition. Big encouragement.")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    if not user.consent_leaderboard:
        card(
            "<b>Leaderboards are off 🔒</b><br>"
            "This is optional. Turn it on in <b>Settings</b> if you want to join.<br>"
            "<span class='ss-muted'>You can still level up normally without competing.</span>",
            panel=True
        )
        return

    card(
        "<b>Friendly reminder 🌼</b><br>"
        "This leaderboard is just for fun. Your progress matters more than your rank.<br>"
        "<span class='ss-muted'>If you opt-out, you’ll disappear after the next refresh.</span>",
        panel=True
    )

    colA, colB, colC = st.columns([0.34, 0.33, 0.33], vertical_alignment="top")

    with colA:
        scope_ui = st.selectbox("Scope", ["Global", "Local"], index=0)
        scope = "global" if scope_ui == "Global" else "local"

    with colB:
        period_ui = st.selectbox("Period", ["Weekly", "All-time"], index=0)
        period = "weekly" if period_ui == "Weekly" else "alltime"

    with colC:
        local_by_ui = st.selectbox("Local group by", ["Region", "City"], index=0)
        local_by = "region" if local_by_ui == "Region" else "city"

    local_value = None
    if scope == "local":
        local_value = (user.region if local_by == "region" else user.city)
        if not local_value:
            st.warning(f"Your {local_by_ui.lower()} is not set. Add it in Settings to use Local leaderboard.")
            scope = "global"  # fallback

    st.markdown("### 📣 Rankings")
    refresh = st.button("Refresh leaderboard ✨", type="primary")

    # Always recalc for now (ensures view stays up to date)
    rows = recalc_leaderboard(
        db=db,
        scope=scope,
        period=period,
        local_by=local_by,
        local_value=local_value,
        limit=50
    )
    db.commit()

    if refresh:
        st.toast("Leaderboard updated!", icon="✅")

    if not rows:
        st.info("No rankings yet. Complete missions and come back soon ✨")
        return

    for r in rows[:50]:
        left, right = st.columns([0.75, 0.25], vertical_alignment="center")
        with left:
            badge = rank_badge(r.rank)
            location_text = ""
            if scope == "local":
                location_text = f" • {local_by_ui}: <b>{local_value}</b>"
            else:
                if r.region:
                    location_text = f" • {r.region}"
                elif r.city:
                    location_text = f" • {r.city}"

            avatar_html = ""
            if r.avatar_url:
                avatar_html = (
                    f"<img src='{r.avatar_url}' alt='avatar' "
                    "style='width:34px;height:34px;border-radius:999px;margin-right:10px;object-fit:cover;'/>"
                )

            card(
                "<div style='display:flex;align-items:center;gap:10px;'>"
                f"{avatar_html}"
                f"<div><b>#{r.rank}</b> @{r.handle} <span class='ss-badge'>{badge}</span>"
                f"<div class='ss-muted'>XP: <b>{r.xp}</b>{location_text}</div></div>"
                "</div>"
            )
        with right:
            if r.user_id == user.id:
                st.success("You")
            else:
                st.caption("👏 Cheer them on!")

    st.markdown("---")
    st.caption("Privacy: Only opted‑in pseudonyms appear. Safety: No messaging here — just friendly ranks.")

main()
