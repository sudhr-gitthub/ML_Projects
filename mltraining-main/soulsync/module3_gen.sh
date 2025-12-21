#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 3 Generator (Map + Opt-in Geolocation + Hidden Mission Unlocks)
# Usage:
#   chmod +x module3_gen.sh
#   ./module3_gen.sh

set -euo pipefail

if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Run this inside your SoulSync repo folder (where app.py exists)."
  exit 1
fi

mkdir -p soulsync/services pages tests

# 1) Append map constants safely (idempotent)
if [ -f "soulsync/constants.py" ] && ! grep -q "MAP_DEFAULT_CENTER" "soulsync/constants.py"; then
cat >> soulsync/constants.py <<'EOT'

# --- Map / Hidden Missions (Module 3) ---

MAP_DEFAULT_CENTER = (20.5937, 78.9629)  # India center (fallback)

# Configured hidden spots (edit these to your real spots!)
# Stored as mission geo_rule_json for each day.
HIDDEN_SPOTS = [
    {
        "title": "🗺️ Hidden: Library Calm Quest (3 deep breaths)",
        "type": "study",
        "difficulty": "medium",
        "xp_reward": 25,
        "rule": {"kind": "radius", "lat": 12.9716, "lon": 77.5946, "radius_m": 250},
        "hint": "A quiet place with books 📚"
    },
    {
        "title": "🗺️ Hidden: Park Power-Up (10-min easy walk)",
        "type": "fitness",
        "difficulty": "medium",
        "xp_reward": 25,
        "rule": {"kind": "radius", "lat": 12.9750, "lon": 77.6050, "radius_m": 300},
        "hint": "Somewhere green 🌿"
    },
]
EOT
echo "✅ Added MAP_DEFAULT_CENTER + HIDDEN_SPOTS to soulsync/constants.py"
else
echo "ℹ️ soulsync/constants.py already has MAP_DEFAULT_CENTER (skipping append)"
fi

# 2) Create soulsync/services/geo.py
cat > soulsync/services/geo.py <<'EOT'
from __future__ import annotations

import json
import math
from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.constants import HIDDEN_SPOTS
from soulsync.models import Mission, MissionAssignment, AuditLog
from soulsync.services.timeutil import today_in_tz


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def ensure_hidden_missions_for_day(db: Session, day):
    """Create hidden mission definitions for a day if missing."""
    existing = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.is_hidden == True,
        Mission.created_by_system == True
    ).count()

    if existing >= len(HIDDEN_SPOTS):
        return

    for spot in HIDDEN_SPOTS:
        geo_rule_json = json.dumps(spot["rule"])
        dupe = db.query(Mission).filter(
            Mission.created_for_date == day,
            Mission.is_hidden == True,
            Mission.title == spot["title"]
        ).one_or_none()
        if dupe:
            continue

        db.add(Mission(
            title=spot["title"],
            type=spot["type"],
            difficulty=spot["difficulty"],
            xp_reward=spot["xp_reward"],
            is_hidden=True,
            geo_rule_json=geo_rule_json,
            created_for_date=day,
            created_by_system=True
        ))
    db.flush()


def _within_radius(rule: dict, lat: float, lon: float) -> bool:
    if rule.get("kind") != "radius":
        return False
    d = haversine_m(lat, lon, float(rule["lat"]), float(rule["lon"]))
    return d <= float(rule["radius_m"])


def find_nearby_hidden_missions(db: Session, day, lat: float, lon: float):
    missions = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.is_hidden == True,
        Mission.created_by_system == True
    ).all()

    nearby = []
    for m in missions:
        if not m.geo_rule_json:
            continue
        try:
            rule = json.loads(m.geo_rule_json)
        except Exception:
            continue

        if _within_radius(rule, lat, lon):
            nearby.append((m, rule))
    return nearby


def unlock_hidden_missions(
    db: Session,
    user_id: int,
    tz_name: str,
    lat: float,
    lon: float,
    max_unlock: int = 3
) -> dict:
    """
    Unlock nearby hidden missions for today.
    Privacy: coordinates are NOT stored; only unlock events are logged.
    """
    day = today_in_tz(tz_name)
    ensure_hidden_missions_for_day(db, day)

    nearby = find_nearby_hidden_missions(db, day, lat, lon)
    if not nearby:
        return {"day": day, "unlocked": [], "message": "No hidden missions nearby right now. Try again later!"}

    unlocked = []
    for m, rule in nearby[:max_unlock]:
        exists = db.query(MissionAssignment).filter(
            MissionAssignment.user_id == user_id,
            MissionAssignment.mission_id == m.id,
            MissionAssignment.date == day
        ).one_or_none()
        if exists:
            continue

        db.add(MissionAssignment(
            user_id=user_id,
            mission_id=m.id,
            date=day,
            status="pending",
            proof_json=None,
            completed_at=None
        ))
        db.flush()

        db.add(AuditLog(
            user_id=user_id,
            event_type="hidden_mission_unlocked",
            meta_json=json.dumps({
                "mission_id": m.id,
                "date": day.isoformat(),
                "rule_kind": rule.get("kind"),
                "radius_m": rule.get("radius_m"),
                "source": "browser_geolocation"
            }),
            created_at=datetime.utcnow()
        ))

        unlocked.append({"mission_id": m.id, "title": m.title})

    db.flush()
    if unlocked:
        return {"day": day, "unlocked": unlocked, "message": f"Unlocked {len(unlocked)} hidden mission(s)! 🎉"}
    return {"day": day, "unlocked": [], "message": "Hidden missions found, but you already unlocked them today ✅"}
EOT

# 3) Update pages/3_🗺️_Map.py
cat > "pages/3_🗺️_Map.py" <<'EOT'
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card
from soulsync.constants import MAP_DEFAULT_CENTER, HIDDEN_SPOTS
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.geo import unlock_hidden_missions

load_css()


def build_map(center_lat: float, center_lon: float, show_spots: bool):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, control_scale=True)

    if show_spots:
        for spot in HIDDEN_SPOTS:
            rule = spot["rule"]
            lat, lon, radius = rule["lat"], rule["lon"], rule["radius_m"]

            folium.Marker(
                [lat, lon],
                tooltip="Mystery Quest Spot ✨",
                popup=spot.get("hint", "A hidden quest lives here!"),
                icon=folium.Icon(color="cadetblue", icon="star", prefix="fa"),
            ).add_to(m)

            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color="#22B8CF",
                fill=True,
                fill_opacity=0.08,
            ).add_to(m)

    return m


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("🗺️ Map", "Unlock hidden missions near configured spots (opt‑in).")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    if not user.consent_location:
        card(
            "<b>Location is off 🔒</b><br>"
            "Hidden missions are optional. You can turn this on in <b>Settings</b>.<br>"
            "<span class='ss-muted'>You can still play daily missions normally — no location needed.</span>",
            panel=True
        )
        center = MAP_DEFAULT_CENTER
        m = build_map(center[0], center[1], show_spots=False)
        st_folium(m, height=520, use_container_width=True)
        return

    card(
        "<b>Privacy promise 🌼</b><br>"
        "We only use your location <b>one time</b> to check if you’re near a quest spot.<br>"
        "<span class='ss-muted'>We store <b>only</b> the unlock event (not your coordinates).</span>",
        panel=True
    )

    st.markdown("### 📍 Share location (one time)")
    st.caption("Your browser will ask permission. You can deny and still play.")

    loc = get_geolocation()

    center_lat, center_lon = MAP_DEFAULT_CENTER
    got_loc = False

    if loc and isinstance(loc, dict) and loc.get("coords"):
        try:
            center_lat = float(loc["coords"]["latitude"])
            center_lon = float(loc["coords"]["longitude"])
            got_loc = True
            st.success("Location received ✅ (not saved)")
        except Exception:
            st.warning("Location data received, but couldn’t read coordinates.")

    st.markdown("### 🌈 Quest Map")
    m = build_map(center_lat, center_lon, show_spots=True)

    if got_loc:
        folium.Marker(
            [center_lat, center_lon],
            tooltip="You are here (not saved)",
            icon=folium.Icon(color="green", icon="user", prefix="fa"),
        ).add_to(m)

    st_folium(m, height=520, use_container_width=True)

    st.markdown("### 🔓 Check for nearby hidden missions")
    if not got_loc:
        st.info("Share location above to check for nearby hidden missions.")
    else:
        if st.button("Scan for hidden quests ✨", type="primary"):
            res = unlock_hidden_missions(
                db=db,
                user_id=user.id,
                tz_name=profile.timezone,
                lat=center_lat,
                lon=center_lon
            )
            db.commit()

            if res["unlocked"]:
                st.balloons()
                st.success(res["message"])
                for u in res["unlocked"]:
                    st.write(f"✅ **Unlocked:** {u['title']}")
                st.info("Go to **✅ Missions** — your hidden quests are now in today’s checklist.")
            else:
                st.warning(res["message"])

    st.markdown("---")
    st.caption("Accessibility: All actions are available via keyboard. Links and buttons have clear labels.")

main()
EOT

# 4) Add tests/test_geo_unlock.py
cat > tests/test_geo_unlock.py <<'EOT'
from datetime import date
import json

from soulsync.models import Mission, MissionAssignment, AuditLog, Profile
from soulsync.services.geo import haversine_m, unlock_hidden_missions


def test_haversine_reasonable():
    assert haversine_m(10.0, 10.0, 10.0, 10.0) < 0.01


def test_unlock_creates_assignment_and_audit(db_session, test_user):
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    prof.timezone = "UTC"
    db_session.commit()

    day = date.today()
    rule = {"kind": "radius", "lat": 10.0, "lon": 10.0, "radius_m": 500}

    m = Mission(
        title="🗺️ Hidden Test Quest",
        type="study",
        difficulty="easy",
        xp_reward=20,
        is_hidden=True,
        geo_rule_json=json.dumps(rule),
        created_for_date=day,
        created_by_system=True
    )
    db_session.add(m)
    db_session.commit()

    res = unlock_hidden_missions(
        db=db_session,
        user_id=test_user.id,
        tz_name="UTC",
        lat=10.0005,
        lon=10.0005
    )
    db_session.commit()

    assert len(res["unlocked"]) >= 1

    a = db_session.query(MissionAssignment).filter_by(user_id=test_user.id, mission_id=m.id, date=day).one_or_none()
    assert a is not None
    assert a.status == "pending"

    logs = db_session.query(AuditLog).filter_by(user_id=test_user.id, event_type="hidden_mission_unlocked").all()
    assert len(logs) >= 1
    meta = logs[-1].meta_json or ""
    assert "latitude" not in meta and "longitude" not in meta and "lat" not in meta and "lon" not in meta
EOT

echo "✅ Module 3 generated/updated successfully."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 3: map + geolocation opt-in + hidden mission unlocks\""
echo "  git push"
echo "Optional:"
echo "  pytest -q"
