STAT_LABELS = {
    "knowledge": "Knowledge",
    "guts": "Guts",
    "proficiency": "Proficiency",
    "kindness": "Kindness",
    "charm": "Charm",
}

STAT_EMOJI = {
    "knowledge": "📚",
    "guts": "🦁",
    "proficiency": "🛠️",
    "kindness": "💛",
    "charm": "✨",
}

MISSION_EMOJI = {
    "study": "📚",
    "fitness": "🏃",
    "sleep": "🌙",
    "nutrition": "🥗",
    "reflection": "🧠",
    "social": "🤝",
}

MAX_LEVEL = 10
XP_BASE = 20

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
