#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 4 Generator (Opt-in Leaderboard + Weekly/All-time + Anti-cheat)
# Usage:
#   chmod +x module4_gen.sh
#   ./module4_gen.sh

set -euo pipefail

if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Run this inside your SoulSync repo folder (where app.py exists)."
  exit 1
fi

mkdir -p soulsync/services pages tests

# 1) soulsync/services/leaderboard.py
cat > soulsync/services/leaderboard.py <<'EOT'
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy.orm import Session

from soulsync.models import User, Profile, AuditLog, RankSnapshot

Scope = Literal["global", "local"]
Period = Literal["weekly", "alltime"]
LocalBy = Literal["city", "region"]

MISSION_EVENT = "mission_completed"

# Gentle anti-cheat defaults (tunable)
MAX_XP_PER_DAY = 600
MAX_MISSIONS_PER_DAY = 18


def _safe_json_loads(s: str | None) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def week_start_utc(dt: datetime | None = None) -> datetime:
    """Monday 00:00 UTC for the week containing dt."""
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    start = dt - timedelta(days=dt.weekday())
    return datetime(start.year, start.month, start.day, tzinfo=timezone.utc)


def _period_since(period: Period, now_utc: datetime) -> datetime | None:
    return week_start_utc(now_utc) if period == "weekly" else None


def _daily_key(dt: datetime) -> str:
    # stored timestamps are naive UTC in our DB; treat them as UTC
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.date().isoformat()


def _local_filter(user: User, local_by: LocalBy, local_value: str | None) -> bool:
    if not local_value:
        return False
    val = local_value.strip().lower()
    if local_by == "city":
        return (user.city or "").strip().lower() == val
    return (user.region or "").strip().lower() == val


@dataclass
class LeaderboardRow:
    user_id: int
    handle: str
    avatar_url: str | None
    xp: int
    rank: int
    city: str | None = None
    region: str | None = None


def _is_suspicious(db: Session, user_id: int, since: datetime | None) -> bool:
    q = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == MISSION_EVENT
    )
    if since is not None:
        q = q.filter(AuditLog.created_at >= since.replace(tzinfo=None))

    logs = q.all()
    if not logs:
        return False

    xp_by_day: dict[str, int] = {}
    missions_by_day: dict[str, int] = {}

    for log in logs:
        day = _daily_key(log.created_at)
        meta = _safe_json_loads(log.meta_json)
        xp_total = int(meta.get("xp_total", 0) or 0)

        xp_by_day[day] = xp_by_day.get(day, 0) + xp_total
        missions_by_day[day] = missions_by_day.get(day, 0) + 1

    if any(xp > MAX_XP_PER_DAY for xp in xp_by_day.values()):
        return True
    if any(cnt > MAX_MISSIONS_PER_DAY for cnt in missions_by_day.values()):
        return True
    return False


def compute_user_xp(db: Session, user_id: int, since: datetime | None) -> int:
    q = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == MISSION_EVENT
    )
    if since is not None:
        q = q.filter(AuditLog.created_at >= since.replace(tzinfo=None))

    total = 0
    for log in q.all():
        meta = _safe_json_loads(log.meta_json)
        total += int(meta.get("xp_total", 0) or 0)
    return total


def cleanup_snapshots_for_optout(db: Session) -> None:
    opted_out_ids = [u.id for u in db.query(User).filter(User.consent_leaderboard == False).all()]
    if not opted_out_ids:
        return
    db.query(RankSnapshot).filter(RankSnapshot.user_id.in_(opted_out_ids)).delete(synchronize_session=False)
    db.flush()


def recalc_leaderboard(
    db: Session,
    scope: Scope,
    period: Period,
    local_by: LocalBy = "region",
    local_value: str | None = None,
    limit: int = 50,
    now_utc: datetime | None = None
) -> list[LeaderboardRow]:
    """Recalculate RankSnapshot and return top rows.

    Rules:
    - Only includes opted-in users.
    - Local scope filters by city/region.
    - Weekly uses Monday 00:00 UTC.
    - Suspicious users are gently excluded.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    since = _period_since(period, now_utc)

    cleanup_snapshots_for_optout(db)

    users = db.query(User).filter(User.consent_leaderboard == True).all()
    if scope == "local":
        users = [u for u in users if _local_filter(u, local_by, local_value)]

    rows: list[LeaderboardRow] = []
    for u in users:
        if _is_suspicious(db, u.id, since):
            continue
        xp = compute_user_xp(db, u.id, since)
        prof = db.query(Profile).filter(Profile.user_id == u.id).one_or_none()
        rows.append(LeaderboardRow(
            user_id=u.id,
            handle=u.handle,
            avatar_url=(prof.avatar_url if prof else None),
            xp=xp,
            rank=0,
            city=u.city,
            region=u.region
        ))

    rows.sort(key=lambda r: (-r.xp, r.handle.lower()))

    for idx, r in enumerate(rows, start=1):
        r.rank = idx

    rows = rows[:limit]

    # Refresh snapshots for this scope/period
    snap_q = db.query(RankSnapshot).filter(RankSnapshot.scope == scope, RankSnapshot.period == period)
    if since is not None:
        snap_q = snap_q.filter(RankSnapshot.created_at >= since.replace(tzinfo=None))
    snap_q.delete(synchronize_session=False)

    for r in rows:
        db.add(RankSnapshot(
            user_id=r.user_id,
            scope=scope,
            period=period,
            xp=r.xp,
            rank=r.rank,
            created_at=now_utc.replace(tzinfo=None)
        ))

    db.flush()
    return rows
EOT

# 2) pages/4_🏆_Leaderboard.py
cat > "pages/4_🏆_Leaderboard.py" <<'EOT'
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
EOT

# 3) tests/test_leaderboard.py
cat > tests/test_leaderboard.py <<'EOT'
import json
from datetime import datetime, timezone, timedelta

from soulsync.models import User, Profile, AuditLog
from soulsync.services.leaderboard import recalc_leaderboard


def add_user(db, email, handle, optin=True, city=None, region=None):
    u = User(email=email, handle=handle, consent_leaderboard=optin, consent_location=False, city=city, region=region)
    db.add(u)
    db.flush()
    db.add(Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}'))
    db.flush()
    return u


def add_xp_log(db, user_id, xp_total, when_utc):
    db.add(AuditLog(
        user_id=user_id,
        event_type="mission_completed",
        meta_json=json.dumps({"xp_total": xp_total}),
        created_at=when_utc.replace(tzinfo=None)
    ))


def test_leaderboard_optin_and_ranking(db_session):
    now = datetime.now(timezone.utc)

    u1 = add_user(db_session, "a@x.com", "Alpha_01", optin=True, region="TN")
    u2 = add_user(db_session, "b@x.com", "Beta_02", optin=True, region="TN")
    u3 = add_user(db_session, "c@x.com", "Gamma_03", optin=False, region="TN")

    add_xp_log(db_session, u1.id, 50, now - timedelta(days=1))
    add_xp_log(db_session, u2.id, 120, now - timedelta(days=1))
    add_xp_log(db_session, u3.id, 999, now - timedelta(days=1))
    db_session.commit()

    rows = recalc_leaderboard(db_session, scope="global", period="alltime", limit=10, now_utc=now)
    db_session.commit()

    handles = [r.handle for r in rows]
    assert "Gamma_03" not in handles
    assert handles[0] == "Beta_02"
    assert handles[1] == "Alpha_01"


def test_optout_disappears_after_refresh(db_session):
    now = datetime.now(timezone.utc)

    u1 = add_user(db_session, "a@x.com", "Alpha_01", optin=True, region="TN")
    add_xp_log(db_session, u1.id, 100, now - timedelta(hours=2))
    db_session.commit()

    rows = recalc_leaderboard(db_session, scope="global", period="weekly", limit=10, now_utc=now)
    db_session.commit()
    assert any(r.handle == "Alpha_01" for r in rows)

    u1.consent_leaderboard = False
    db_session.commit()

    rows2 = recalc_leaderboard(db_session, scope="global", period="weekly", limit=10, now_utc=now)
    db_session.commit()
    assert all(r.handle != "Alpha_01" for r in rows2)
EOT

# Done

echo "✅ Module 4 generated/updated successfully."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 4: leaderboard opt-in + weekly/all-time\""
echo "  git push"
echo "Optional:"
echo "  pytest -q"
