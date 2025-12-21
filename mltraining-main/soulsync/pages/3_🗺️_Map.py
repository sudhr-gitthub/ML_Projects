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
