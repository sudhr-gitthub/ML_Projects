#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 6 Generator (Minimal Export + Delete Controls)
# Usage:
#   chmod +x module6_gen.sh
#   ./module6_gen.sh

set -euo pipefail

if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Run this inside your SoulSync repo folder (where app.py exists)."
  exit 1
fi

mkdir -p soulsync/services pages tests

# 1) soulsync/services/export.py (MINIMAL export by default)
cat > soulsync/services/export.py <<'EOT'
from __future__ import annotations

import json
from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.models import (
    User, Profile, Stat,
    Mission, MissionAssignment,
    JournalEntry, VoiceMemory
)


def _dt(x):
    if not x:
        return None
    if isinstance(x, datetime):
        return x.isoformat()
    return str(x)


def export_user_data_minimal(db: Session, user_id: int) -> dict:
    """Minimal export (default): profile, stats, missions/assignments, journal, voice_memory.

    Excludes by default:
    - VoiceMessage chat history
    - AuditLog
    """
    user = db.query(User).filter(User.id == user_id).one()

    profile = db.query(Profile).filter(Profile.user_id == user_id).one_or_none()
    stats = db.query(Stat).filter(Stat.user_id == user_id).all()

    assignments = (
        db.query(MissionAssignment, Mission)
        .join(Mission, Mission.id == MissionAssignment.mission_id)
        .filter(MissionAssignment.user_id == user_id)
        .order_by(MissionAssignment.date.asc())
        .all()
    )

    journal = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.asc())
        .all()
    )

    voice_memory = (
        db.query(VoiceMemory)
        .filter(VoiceMemory.user_id == user_id)
        .order_by(VoiceMemory.created_at.asc())
        .all()
    )

    out = {
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "handle": user.handle,
            "consent_leaderboard": user.consent_leaderboard,
            "consent_location": user.consent_location,
            "city": user.city,
            "region": user.region,
            "created_at": _dt(user.created_at),
        },
        "profile": None if not profile else {
            "avatar_url": profile.avatar_url,
            "goals_json": profile.goals_json,
            "timezone": profile.timezone,
            "streak_count": profile.streak_count,
            "last_login_at": _dt(profile.last_login_at),
        },
        "stats": [
            {
                "type": s.type,
                "level": s.level,
                "xp": s.xp,
                "updated_at": _dt(s.updated_at),
            } for s in stats
        ],
        "missions": [
            {
                "assignment": {
                    "id": a.id,
                    "date": str(a.date),
                    "status": a.status,
                    "proof_json": a.proof_json,
                    "completed_at": _dt(a.completed_at),
                },
                "mission": {
                    "id": m.id,
                    "title": m.title,
                    "type": m.type,
                    "difficulty": m.difficulty,
                    "xp_reward": m.xp_reward,
                    "is_hidden": m.is_hidden,
                    # No user coordinates are stored; include rule only as stored in mission.
                    "geo_rule_json": m.geo_rule_json if m.is_hidden else None,
                    "created_for_date": str(m.created_for_date),
                    "created_by_system": m.created_by_system,
                }
            } for (a, m) in assignments
        ],
        "journal": [
            {
                "id": j.id,
                "mood": j.mood,
                "text": j.text,
                "tags": j.tags,
                "created_at": _dt(j.created_at),
            } for j in journal
        ],
        "voice_memory": [
            {
                "id": vm.id,
                "kind": vm.kind,
                "content": vm.content,
                "created_at": _dt(vm.created_at),
                "updated_at": _dt(vm.updated_at),
                "has_vector": bool(vm.vector),
            } for vm in voice_memory
        ],
    }

    return out


def export_user_json_bytes(db: Session, user_id: int) -> bytes:
    data = export_user_data_minimal(db, user_id)
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
EOT

# 2) soulsync/services/account.py (delete controls)
cat > soulsync/services/account.py <<'EOT'
from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.models import (
    User, Profile, Stat,
    MissionAssignment,
    JournalEntry, VoiceMessage, VoiceMemory,
    RankSnapshot, AuditLog
)


def delete_voice_history(db: Session, user_id: int) -> int:
    """Delete VoiceMessage rows for user. Returns count deleted."""
    q = db.query(VoiceMessage).filter(VoiceMessage.user_id == user_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.flush()
    db.add(AuditLog(user_id=user_id, event_type="voice_history_deleted", meta_json=None, created_at=datetime.utcnow()))
    db.flush()
    return count


def delete_voice_memory(db: Session, user_id: int) -> int:
    """Delete VoiceMemory rows for user. Returns count deleted."""
    q = db.query(VoiceMemory).filter(VoiceMemory.user_id == user_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.flush()
    db.add(AuditLog(user_id=user_id, event_type="voice_memory_deleted", meta_json=None, created_at=datetime.utcnow()))
    db.flush()
    return count


def delete_account(db: Session, user_id: int) -> None:
    """Full wipe of user-related data."""
    db.query(RankSnapshot).filter(RankSnapshot.user_id == user_id).delete(synchronize_session=False)

    db.query(MissionAssignment).filter(MissionAssignment.user_id == user_id).delete(synchronize_session=False)
    db.query(JournalEntry).filter(JournalEntry.user_id == user_id).delete(synchronize_session=False)
    db.query(VoiceMessage).filter(VoiceMessage.user_id == user_id).delete(synchronize_session=False)
    db.query(VoiceMemory).filter(VoiceMemory.user_id == user_id).delete(synchronize_session=False)

    db.query(Stat).filter(Stat.user_id == user_id).delete(synchronize_session=False)
    db.query(Profile).filter(Profile.user_id == user_id).delete(synchronize_session=False)

    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete(synchronize_session=False)

    u = db.query(User).filter(User.id == user_id).one_or_none()
    if u:
        db.delete(u)

    db.flush()
EOT

# 3) Update pages/7_⚙️_Settings.py (export + delete)
cat > "pages/7_⚙️_Settings.py" <<'EOT'
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
EOT

# 4) tests/test_export_delete.py (minimal export + delete)
cat > tests/test_export_delete.py <<'EOT'
from datetime import date
import json

from soulsync.models import (
    User, Profile, Stat,
    Mission, MissionAssignment,
    JournalEntry, VoiceMemory, VoiceMessage
)
from soulsync.services.export import export_user_data_minimal
from soulsync.services.account import delete_account


def test_export_contains_required_sections_and_is_minimal(db_session):
    u = User(email="exp@x.com", handle="Exporter_01", consent_leaderboard=False, consent_location=False)
    db_session.add(u)
    db_session.flush()

    db_session.add(Profile(user_id=u.id, timezone="UTC", streak_count=2, goals_json='{"goals":["Study smarter"],"note":""}'))
    db_session.add(Stat(user_id=u.id, type="knowledge", level=2, xp=5))
    db_session.flush()

    m = Mission(title="Test Mission", type="study", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=date.today(), created_by_system=True)
    db_session.add(m)
    db_session.flush()

    db_session.add(MissionAssignment(user_id=u.id, mission_id=m.id, date=date.today(), status="pending"))
    db_session.add(JournalEntry(user_id=u.id, mood="okay", text="Hello journal", tags="test"))
    db_session.add(VoiceMemory(user_id=u.id, kind="journal", content="Memory content", vector=None))

    # chat history exists but must NOT be exported
    db_session.add(VoiceMessage(user_id=u.id, role="user", text="Hi", embedding_vector=None))

    db_session.commit()

    data = export_user_data_minimal(db_session, u.id)

    assert "user" in data
    assert "profile" in data
    assert "stats" in data
    assert "missions" in data
    assert "journal" in data
    assert "voice_memory" in data

    assert "voice_messages" not in data
    assert "audit_log" not in data


def test_delete_account_wipes_everything(db_session):
    u = User(email="del@x.com", handle="DeleteMe_01", consent_leaderboard=True, consent_location=True)
    db_session.add(u)
    db_session.flush()

    db_session.add(Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Sleep better"],"note":""}'))
    db_session.add(Stat(user_id=u.id, type="knowledge", level=1, xp=0))
    db_session.commit()

    delete_account(db_session, u.id)
    db_session.commit()

    assert db_session.query(User).filter(User.id == u.id).one_or_none() is None
    assert db_session.query(Profile).filter(Profile.user_id == u.id).one_or_none() is None
    assert db_session.query(Stat).filter(Stat.user_id == u.id).count() == 0
EOT


echo "✅ Module 6 generated/updated successfully."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 6: minimal export + delete controls\""
echo "  git push"
echo "Optional:"
echo "  pytest -q"
