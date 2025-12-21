#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 2 Generator (Onboarding + Stats + Daily Missions)
# Usage:
#   chmod +x module2_gen.sh
#   ./module2_gen.sh

set -euo pipefail

# --- sanity checks ---
if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Please run this inside your SoulSync repo folder."
  echo "   Example: cd ~/soulsync/YOUR_REPO"
  exit 1
fi

mkdir -p soulsync/services pages tests

# 1) soulsync/services/__init__.py
cat > soulsync/services/__init__.py <<'EOT'
__all__ = []
EOT

# 2) soulsync/services/users.py
cat > soulsync/services/users.py <<'EOT'
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from soulsync.models import User, Profile, Stat, STAT_TYPES

def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).one()

def ensure_profile(db: Session, user_id: int) -> Profile:
    prof = db.query(Profile).filter(Profile.user_id == user_id).one_or_none()
    if prof is None:
        prof = Profile(user_id=user_id, timezone="UTC", streak_count=0, last_login_at=datetime.utcnow())
        db.add(prof)
        db.flush()
    return prof

def ensure_all_stats(db: Session, user_id: int) -> None:
    existing = {s.type for s in db.query(Stat).filter(Stat.user_id == user_id).all()}
    for t in STAT_TYPES:
        if t not in existing:
            db.add(Stat(user_id=user_id, type=t, level=1, xp=0))
    db.flush()

def is_onboarded(profile: Profile) -> bool:
    return bool(profile.goals_json and profile.timezone)
EOT

# 3) soulsync/services/timeutil.py
cat > soulsync/services/timeutil.py <<'EOT'
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

def now_in_tz(tz_name: str):
    tz = ZoneInfo(tz_name or "UTC")
    return datetime.now(tz)

def today_in_tz(tz_name: str):
    return now_in_tz(tz_name).date()
EOT

# 4) soulsync/services/stats.py
cat > soulsync/services/stats.py <<'EOT'
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from soulsync.constants import XP_BASE, MAX_LEVEL
from soulsync.models import Stat

def xp_needed_for_level(level: int, base: int = XP_BASE) -> int:
    """XP needed to advance from level -> level+1 using base*n^2."""
    n = max(1, int(level))
    return int(base * (n ** 2))

def apply_xp_and_level(stat: Stat, xp_gain: int, base: int = XP_BASE) -> Stat:
    if xp_gain <= 0:
        return stat
    stat.xp += int(xp_gain)
    while stat.level < MAX_LEVEL:
        need = xp_needed_for_level(stat.level, base=base)
        if stat.xp >= need:
            stat.xp -= need
            stat.level += 1
        else:
            break
    stat.updated_at = datetime.utcnow()
    return stat

def get_or_create_stat(db: Session, user_id: int, stat_type: str) -> Stat:
    st = db.query(Stat).filter(Stat.user_id == user_id, Stat.type == stat_type).one_or_none()
    if st:
        return st
    st = Stat(user_id=user_id, type=stat_type, level=1, xp=0)
    db.add(st)
    db.flush()
    return st

def grant_stat_xp(db: Session, user_id: int, stat_type: str, xp_gain: int) -> Stat:
    st = get_or_create_stat(db, user_id, stat_type)
    st = apply_xp_and_level(st, xp_gain)
    db.add(st)
    return st
EOT

# 5) soulsync/services/missions.py
cat > soulsync/services/missions.py <<'EOT'
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from soulsync.models import Mission, MissionAssignment, Profile, AuditLog
from soulsync.services.stats import grant_stat_xp
from soulsync.services.timeutil import today_in_tz

MISSION_CATALOG = [
    ("📚 Study sprint: 20 minutes (timer)", "study", "easy", 15),
    ("📚 Review notes for 15 minutes", "study", "easy", 12),
    ("📚 Practice 5 problems or questions", "study", "medium", 18),

    ("🏃 Move: 10-minute walk or stretch", "fitness", "easy", 12),
    ("🏃 Move: 15 minutes (your choice)", "fitness", "medium", 18),
    ("🏃 Try a short strength set (5–10 mins)", "fitness", "hard", 25),

    ("🌙 Screen-off 30 minutes before bed", "sleep", "medium", 18),
    ("🌙 Plan bedtime + wake time (write it)", "sleep", "easy", 12),

    ("🥗 Add one fruit/veg today", "nutrition", "easy", 12),
    ("🥗 Drink an extra glass of water", "nutrition", "easy", 10),
    ("🥗 Build a balanced plate (photo optional)", "nutrition", "medium", 18),

    ("🧠 3 lines: what went well today?", "reflection", "easy", 12),
    ("🧠 Name 1 worry + 1 tiny next step", "reflection", "medium", 18),

    ("🤝 Send a kind message to someone", "social", "easy", 12),
    ("🤝 Help at home for 10 minutes", "social", "medium", 18),
]

MISSION_TO_STAT = {
    "study": "knowledge",
    "fitness": "guts",
    "sleep": "proficiency",
    "nutrition": "kindness",
    "reflection": "charm",
    "social": "kindness",
}

def _pick_daily_set(seed_key: str, count: int = 5):
    rng = random.Random(seed_key)
    pool = MISSION_CATALOG[:]
    rng.shuffle(pool)

    chosen = []
    needed_types = ["study", "fitness", "sleep", "nutrition", "reflection"]
    for t in needed_types:
        for item in pool:
            if item[1] == t and item not in chosen:
                chosen.append(item)
                break

    for item in pool:
        if len(chosen) >= count:
            break
        if item not in chosen:
            chosen.append(item)

    return chosen[:count]

def ensure_daily_missions_exist(db: Session, for_date):
    existing = db.query(Mission).filter(
        Mission.created_for_date == for_date,
        Mission.created_by_system == True,
        Mission.is_hidden == False,
    ).count()

    if existing >= 5:
        return

    seed_key = f"{for_date.isoformat()}-soulsync"
    daily = _pick_daily_set(seed_key, count=5)

    for title, mtype, diff, xp in daily:
        db.add(Mission(
            title=title,
            type=mtype,
            difficulty=diff,
            xp_reward=xp,
            is_hidden=False,
            geo_rule_json=None,
            created_for_date=for_date,
            created_by_system=True
        ))
    db.flush()

def ensure_assignments_for_user(db: Session, user_id: int, tz_name: str):
    day = today_in_tz(tz_name)
    ensure_daily_missions_exist(db, day)

    missions = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.created_by_system == True,
        Mission.is_hidden == False,
    ).all()

    existing = {
        (a.mission_id, a.date)
        for a in db.query(MissionAssignment).filter(
            MissionAssignment.user_id == user_id,
            MissionAssignment.date == day
        ).all()
    }

    for m in missions:
        if (m.id, day) not in existing:
            db.add(MissionAssignment(
                user_id=user_id,
                mission_id=m.id,
                date=day,
                status="pending",
                proof_json=None,
                completed_at=None
            ))
    db.flush()
    return day

def _streak_bonus_multiplier(streak_count: int) -> float:
    if streak_count <= 0:
        return 0.0
    return min(0.30, 0.05 * streak_count)

def _update_streak_for_day(db: Session, user_id: int, day):
    prof = db.query(Profile).filter(Profile.user_id == user_id).one()
    todays = db.query(MissionAssignment).filter(
        MissionAssignment.user_id == user_id,
        MissionAssignment.date == day
    ).all()

    if not todays:
        return
    if not all(x.status == "completed" for x in todays):
        return

    yesterday = day - timedelta(days=1)
    y_assign = db.query(MissionAssignment).filter(
        MissionAssignment.user_id == user_id,
        MissionAssignment.date == yesterday
    ).all()

    y_done = bool(y_assign) and all(x.status == "completed" for x in y_assign)

    if y_done:
        prof.streak_count += 1
    else:
        prof.streak_count = max(1, prof.streak_count)

    db.add(AuditLog(
        user_id=user_id,
        event_type="streak_updated",
        meta_json=json.dumps({"date": day.isoformat(), "streak": prof.streak_count})
    ))
    db.flush()

def complete_assignment(db: Session, assignment_id: int, user_id: int, proof: dict | None = None) -> dict:
    a = db.query(MissionAssignment).filter(
        MissionAssignment.id == assignment_id,
        MissionAssignment.user_id == user_id
    ).one()

    if a.status == "completed":
        return {"ok": True, "message": "Already completed."}

    m = db.query(Mission).filter(Mission.id == a.mission_id).one()
    prof = db.query(Profile).filter(Profile.user_id == user_id).one()

    bonus_mult = _streak_bonus_multiplier(prof.streak_count)
    bonus = int(round(m.xp_reward * bonus_mult))
    total_xp = m.xp_reward + bonus

    stat_type = MISSION_TO_STAT.get(m.type, "knowledge")
    grant_stat_xp(db, user_id, stat_type, total_xp)

    a.status = "completed"
    a.completed_at = datetime.utcnow()
    a.proof_json = json.dumps(proof or {})

    db.add(AuditLog(
        user_id=user_id,
        event_type="mission_completed",
        meta_json=json.dumps({
            "assignment_id": assignment_id,
            "mission_id": m.id,
            "xp_base": m.xp_reward,
            "xp_bonus": bonus,
            "xp_total": total_xp,
            "stat_type": stat_type
        })
    ))
    db.flush()

    _update_streak_for_day(db, user_id, a.date)

    return {"ok": True, "message": f"+{total_xp} XP to {stat_type} (base {m.xp_reward} + bonus {bonus})"}

def get_todays_assignments(db: Session, user_id: int, tz_name: str):
    day = ensure_assignments_for_user(db, user_id, tz_name)
    rows = (
        db.query(MissionAssignment, Mission)
        .join(Mission, Mission.id == MissionAssignment.mission_id)
        .filter(MissionAssignment.user_id == user_id, MissionAssignment.date == day)
        .order_by(Mission.difficulty.asc())
        .all()
    )
    return day, rows
EOT

# 6) pages/1_🏠_Dashboard.py
cat > "pages/1_🏠_Dashboard.py" <<'EOT'
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
EOT

# 7) pages/2_✅_Missions.py
cat > "pages/2_✅_Missions.py" <<'EOT'
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
EOT

# 8) pages/7_⚙️_Settings.py
cat > "pages/7_⚙️_Settings.py" <<'EOT'
import json
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.services.users import get_user, ensure_profile

load_css()

def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)

    page_header("⚙️ Settings", "Privacy controls and personalization")

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
    st.markdown("### Safety")
    st.info(
        "SoulSync is supportive, not medical advice. "
        "If you feel unsafe or might hurt yourself, contact local emergency services or a trusted adult right away."
    )

main()
EOT

# 9) tests/conftest.py
cat > tests/conftest.py <<'EOT'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from soulsync.models import Base, User, Profile

@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    yield session
    session.close()

@pytest.fixture()
def test_user(db_session):
    u = User(email="test@example.com", handle="Tester_01", consent_leaderboard=False, consent_location=False)
    db_session.add(u)
    db_session.flush()
    p = Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}')
    db_session.add(p)
    db_session.commit()
    return u
EOT

# 10) tests/test_xp_curve.py
cat > tests/test_xp_curve.py <<'EOT'
from soulsync.services.stats import xp_needed_for_level, apply_xp_and_level
from soulsync.models import Stat

def test_xp_needed_curve_base_n2():
    assert xp_needed_for_level(1) == 20
    assert xp_needed_for_level(2) == 80
    assert xp_needed_for_level(3) == 180

def test_apply_xp_levels_up():
    s = Stat(user_id=1, type="knowledge", level=1, xp=0)
    apply_xp_and_level(s, 25)
    assert s.level == 2
    assert s.xp == 5

    apply_xp_and_level(s, 90)
    assert s.level == 3
    assert s.xp == 15
EOT

# 11) tests/test_missions.py
cat > tests/test_missions.py <<'EOT'
from datetime import date
from soulsync.models import Mission, MissionAssignment, Stat, Profile
from soulsync.services.missions import complete_assignment
from soulsync.services.users import ensure_all_stats

def setup_day(db, user_id: int, day: date):
    m1 = Mission(title="Study", type="study", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=day, created_by_system=True)
    m2 = Mission(title="Sleep", type="sleep", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=day, created_by_system=True)
    db.add_all([m1, m2])
    db.flush()

    a1 = MissionAssignment(user_id=user_id, mission_id=m1.id, date=day, status="pending")
    a2 = MissionAssignment(user_id=user_id, mission_id=m2.id, date=day, status="pending")
    db.add_all([a1, a2])
    db.flush()
    return a1, a2

def test_complete_assignment_grants_xp_and_updates_status(db_session, test_user):
    ensure_all_stats(db_session, test_user.id)
    db_session.commit()

    day = date(2025, 1, 1)
    a1, a2 = setup_day(db_session, test_user.id, day)
    db_session.commit()

    res = complete_assignment(db_session, a1.id, test_user.id, proof={"kind": "note", "value": "done"})
    db_session.commit()
    assert res["ok"] is True

    a1_db = db_session.query(MissionAssignment).filter_by(id=a1.id).one()
    assert a1_db.status == "completed"

    stat = db_session.query(Stat).filter_by(user_id=test_user.id, type="knowledge").one()
    assert stat.xp >= 10

def test_streak_increments_only_when_all_done(db_session, test_user):
    ensure_all_stats(db_session, test_user.id)
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    prof.streak_count = 0
    db_session.commit()

    day = date(2025, 1, 2)
    a1, a2 = setup_day(db_session, test_user.id, day)
    db_session.commit()

    complete_assignment(db_session, a1.id, test_user.id, proof=None)
    db_session.commit()

    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    assert prof.streak_count == 0

    complete_assignment(db_session, a2.id, test_user.id, proof=None)
    db_session.commit()

    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    assert prof.streak_count == 1
EOT

echo "✅ Module 2 generated successfully."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 2: onboarding + stats + daily missions\""
echo "  git push"
echo "Optional:"
echo "  pytest -q"
