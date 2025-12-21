#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 5 Generator (Your Voice: RAG + HF Inference + Moderation + Memory + Journal)
# Usage:
#   chmod +x module5_gen.sh
#   ./module5_gen.sh

set -euo pipefail

if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Run this inside your SoulSync repo folder (where app.py exists)."
  exit 1
fi

mkdir -p soulsync/services pages tests

# 1) soulsync/services/moderation.py
cat > soulsync/services/moderation.py <<'EOT'
from __future__ import annotations
from dataclasses import dataclass

# Simple keyword lists (conservative; expand cautiously)
TOXIC_WORDS = {
    "idiot", "stupid", "hate you", "kill yourself", "loser", "dumb", "shut up",
    "worthless", "ugly", "moron"
}

# Self-harm / crisis signals (very conservative)
SELF_HARM_PHRASES = {
    "i want to die", "i want to kill myself", "suicide", "self harm", "hurt myself",
    "end it all", "no reason to live"
}

# Sexual content keywords (block)
SEXUAL_TERMS = {
    "porn", "sex", "nude", "naked", "erotic", "masturbat", "blowjob", "anal",
    "hook up", "onlyfans"
}

@dataclass
class ModResult:
    ok: bool
    flagged: bool
    category: str | None = None  # toxic | self_harm | sexual
    message: str | None = None

CRISIS_RESOURCES_TEXT = (
    "If you feel unsafe or might hurt yourself, please reach out now:\n"
    "• India (Govt): KIRAN 1800-599-0019 (24x7)\n"
    "• AASRA: 022 2754 6669 (24x7)\n"
    "Or talk to a trusted adult / local emergency services."
)

DISCLAIMER_TEXT = (
    "⚠️ SoulSync is supportive and non‑clinical. It can’t provide medical advice. "
    "If you’re in danger or feel like hurting yourself, contact local emergency services or a trusted adult."
)


def _contains_any(text: str, phrases: set[str]) -> bool:
    t = (text or "").lower()
    return any(p in t for p in phrases)


def moderate_text(text: str) -> ModResult:
    """Rule-based moderation gate."""
    t = (text or "").strip().lower()
    if not t:
        return ModResult(ok=True, flagged=False)

    if _contains_any(t, SEXUAL_TERMS):
        return ModResult(
            ok=False, flagged=True, category="sexual",
            message="I can’t help with sexual content. If you’d like, tell me about your goals or how your day went 🌼"
        )

    if _contains_any(t, SELF_HARM_PHRASES):
        return ModResult(
            ok=False, flagged=True, category="self_harm",
            message=f"{DISCLAIMER_TEXT}\n\n{CRISIS_RESOURCES_TEXT}"
        )

    if _contains_any(t, TOXIC_WORDS):
        return ModResult(
            ok=False, flagged=True, category="toxic",
            message="Let’s keep it kind 🌟. Can you rephrase that in a calmer way? I’m here to help."
        )

    return ModResult(ok=True, flagged=False)
EOT

# 2) soulsync/services/embeddings.py
cat > soulsync/services/embeddings.py <<'EOT'
from __future__ import annotations

import os
import numpy as np
from functools import lru_cache

MODEL_NAME_DEFAULT = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_embedder():
    """Lazy-load embedder model."""
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBED_MODEL_ID", MODEL_NAME_DEFAULT)
    return SentenceTransformer(model_name)


def embed_text(text: str) -> np.ndarray:
    emb = get_embedder().encode([text], normalize_embeddings=True)
    return np.array(emb[0], dtype=np.float32)


def serialize_vector(vec: np.ndarray) -> bytes:
    vec = np.asarray(vec, dtype=np.float32)
    return vec.tobytes()


def deserialize_vector(blob: bytes, dim: int) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.float32)
    if dim and arr.size != dim:
        return arr
    return arr
EOT

# 3) soulsync/services/journal.py
cat > soulsync/services/journal.py <<'EOT'
from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.models import JournalEntry, VoiceMemory
from soulsync.services.embeddings import embed_text, serialize_vector


def add_journal_entry(db: Session, user_id: int, mood: str, text: str, tags: str | None = None) -> JournalEntry:
    je = JournalEntry(user_id=user_id, mood=mood, text=text, tags=tags, created_at=datetime.utcnow())
    db.add(je)
    db.flush()

    # Mirror into voice memory for RAG
    vec = embed_text(f"[Journal/{mood}] {text}")
    vm = VoiceMemory(
        user_id=user_id,
        kind="journal",
        content=f"[Mood: {mood}] {text}" + (f" (tags: {tags})" if tags else ""),
        vector=serialize_vector(vec),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(vm)
    db.flush()
    return je
EOT

# 4) soulsync/services/voice.py
cat > soulsync/services/voice.py <<'EOT'
from __future__ import annotations

import os
import json
import requests
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from soulsync.models import VoiceMessage, VoiceMemory, JournalEntry, AuditLog
from soulsync.services.embeddings import embed_text, serialize_vector, deserialize_vector
from soulsync.services.moderation import moderate_text, DISCLAIMER_TEXT

DEFAULT_MODEL_ID = os.getenv("LLM_MODEL_ID", "microsoft/phi-3-mini-4k-instruct")
HF_API_KEY = os.getenv("HF_API_KEY")

MAX_MSG_PER_5MIN = 10


def _hf_generate(prompt: str, model_id: str = DEFAULT_MODEL_ID) -> str:
    if not HF_API_KEY:
        raise RuntimeError("HF_API_KEY missing")

    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 220,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

    r = requests.post(url, headers=headers, json=payload, timeout=45)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list) and data and isinstance(data[0], dict):
        return (data[0].get("generated_text") or "").strip()
    if isinstance(data, dict) and "generated_text" in data:
        return (data["generated_text"] or "").strip()
    return str(data)[:2000].strip()


def _fallback_reply(user_text: str, context_hint: str = "") -> str:
    starters = [
        "I’m glad you told me 🌟",
        "Thanks for sharing — that matters 💛",
        "Okay, let’s do this step by step ✨",
    ]
    tip = "Pick ONE tiny action you can do in 5 minutes."
    return f"{np.random.choice(starters)}\n\n{context_hint}\n\n**Tiny next step:** {tip}"


def _safe_json_loads(s: str | None) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def _summarize_recent_missions(db: Session, user_id: int, limit: int = 6) -> list[str]:
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == "mission_completed"
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()

    out = []
    for log in logs:
        meta = _safe_json_loads(log.meta_json)
        stat = meta.get("stat_type", "stat")
        xp = meta.get("xp_total", 0)
        out.append(f"- Completed a mission (+{xp} XP to {stat})")
    return out


def _recent_journal(db: Session, user_id: int, limit: int = 3) -> list[str]:
    rows = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id
    ).order_by(JournalEntry.created_at.desc()).limit(limit).all()
    return [f"- [Mood: {r.mood}] {r.text}" for r in rows]


def _retrieve_memories(db: Session, user_id: int, query_vec: np.ndarray, top_k: int = 4) -> list[str]:
    mems = db.query(VoiceMemory).filter(VoiceMemory.user_id == user_id).all()
    if not mems:
        return []

    dim = int(query_vec.size)
    scored = []
    for m in mems:
        if not m.vector:
            continue
        vec = deserialize_vector(m.vector, dim=dim)
        sim = float(np.dot(query_vec, vec) / (np.linalg.norm(vec) + 1e-8))
        scored.append((sim, m.content, m.kind, m.updated_at or m.created_at))

    scored.sort(key=lambda x: (x[0], x[3]), reverse=True)
    return [f"- ({kind}) {content}" for sim, content, kind, _ in scored[:top_k] if sim > 0.15]


def build_rag_context(db: Session, user_id: int, user_text: str) -> str:
    qv = embed_text(user_text)
    memories = _retrieve_memories(db, user_id, qv, top_k=4)
    missions = _summarize_recent_missions(db, user_id, limit=5)
    journal = _recent_journal(db, user_id, limit=3)

    sections = []
    if memories:
        sections.append("MEMORY:\n" + "\n".join(memories))
    if missions:
        sections.append("RECENT MISSIONS:\n" + "\n".join(missions))
    if journal:
        sections.append("RECENT JOURNAL:\n" + "\n".join(journal))

    return "\n\n".join(sections).strip()


def build_prompt(user_text: str, rag_context: str) -> str:
    system = (
        "You are 'Your Voice', a cheerful supportive digital twin in a student-friendly life RPG.\n"
        "Audience: ages 13–14. Use simple, encouraging language.\n"
        "Rules:\n"
        "- Be supportive and non-clinical. Do not give medical advice.\n"
        "- Prefer tiny actionable steps (5–15 minutes).\n"
        "- Reference only the provided CONTEXT if relevant.\n"
        "- Avoid shaming. Use warm, optimistic tone.\n"
    )

    context_block = f"CONTEXT:\n{rag_context}\n" if rag_context else "CONTEXT: (none)\n"
    return f"{system}\n{context_block}\nUSER:\n{user_text}\nASSISTANT:\n"


def save_message(db: Session, user_id: int, role: str, text: str):
    vec = None
    try:
        vec_arr = embed_text(text)
        vec = serialize_vector(vec_arr)
    except Exception:
        vec = None

    msg = VoiceMessage(
        user_id=user_id,
        role=role,
        text=text,
        created_at=datetime.utcnow(),
        embedding_vector=vec
    )
    db.add(msg)
    db.flush()
    return msg


def chat_once(db: Session, user_id: int, user_text: str, model_id: str = DEFAULT_MODEL_ID) -> dict:
    mod = moderate_text(user_text)
    if mod.flagged:
        save_message(db, user_id, "user", user_text)
        safe = mod.message or "Let’s keep things safe and kind."
        save_message(db, user_id, "assistant", safe)
        return {"ok": False, "assistant": safe, "flagged": True, "category": mod.category}

    rag = build_rag_context(db, user_id, user_text)
    prompt = build_prompt(user_text, rag)

    save_message(db, user_id, "user", user_text)

    try:
        if HF_API_KEY:
            out = _hf_generate(prompt, model_id=model_id)
            if not out:
                out = _fallback_reply(user_text, context_hint="I’m here with you.")
        else:
            out = _fallback_reply(user_text, context_hint="(Tip: Add HF_API_KEY for smarter replies.)")
    except Exception:
        out = _fallback_reply(user_text, context_hint="(AI is resting — but I can still help!)")

    out_final = f"{out}\n\n{DISCLAIMER_TEXT}"

    save_message(db, user_id, "assistant", out_final)
    return {"ok": True, "assistant": out_final, "flagged": False}


def get_conversation(db: Session, user_id: int, limit: int = 50):
    return db.query(VoiceMessage).filter(
        VoiceMessage.user_id == user_id
    ).order_by(VoiceMessage.created_at.asc()).limit(limit).all()


def list_memory(db: Session, user_id: int, limit: int = 50):
    return db.query(VoiceMemory).filter(
        VoiceMemory.user_id == user_id
    ).order_by(VoiceMemory.updated_at.desc()).limit(limit).all()


def delete_memory_item(db: Session, user_id: int, mem_id: int) -> bool:
    m = db.query(VoiceMemory).filter(
        VoiceMemory.user_id == user_id,
        VoiceMemory.id == mem_id
    ).one_or_none()
    if not m:
        return False
    db.delete(m)
    db.flush()
    return True
EOT

# 5) Update pages/5_📓_Journal.py
cat > "pages/5_📓_Journal.py" <<'EOT'
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import card
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.journal import add_journal_entry
from soulsync.models import JournalEntry

load_css()

MOODS = ["great", "good", "okay", "low", "rough"]


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("📓 Journal", "A tiny reflection helps Your Voice support you better ✨")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    card(
        "<b>Tip:</b> Keep it simple — 3 lines is enough.<br>"
        "<span class='ss-muted'>Journal entries become private memory snippets for Your Voice (you can delete them).</span>",
        panel=True
    )

    with st.form("journal"):
        mood = st.selectbox("Mood", MOODS, index=2)
        text = st.text_area("What happened today?", placeholder="Example: I studied 20 mins, then got distracted…", height=120)
        tags = st.text_input("Tags (optional)", placeholder="study, friends, sleep")
        saved = st.form_submit_button("Save entry ✅", type="primary")

    if saved:
        if not text.strip():
            st.warning("Write at least one sentence ✍️")
        else:
            add_journal_entry(db, user.id, mood, text.strip(), tags.strip() or None)
            db.commit()
            st.success("Saved! Your Voice can now reference this 🧠✨")

    st.markdown("---")
    st.markdown("### Recent entries")
    rows = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).order_by(JournalEntry.created_at.desc()).limit(10).all()
    if not rows:
        st.info("No entries yet — try adding one above!")
    for r in rows:
        card(f"<b>{r.mood.upper()}</b> • <span class='ss-muted'>{r.created_at}</span><br>{r.text}")

main()
EOT

# 6) Update pages/6_💬_Your_Voice.py
cat > "pages/6_💬_Your_Voice.py" <<'EOT'
import time
import streamlit as st

from soulsync.db import get_session
from soulsync.ui.styles import load_css, page_header
from soulsync.ui.components import bubble, card
from soulsync.services.users import get_user, ensure_profile, is_onboarded
from soulsync.services.voice import chat_once, get_conversation, list_memory, delete_memory_item, MAX_MSG_PER_5MIN
from soulsync.services.moderation import CRISIS_RESOURCES_TEXT

load_css()


def _rate_limit_ok():
    now = time.time()
    history = st.session_state.get("voice_msg_times", [])
    history = [t for t in history if now - t < 300]
    st.session_state["voice_msg_times"] = history
    if len(history) >= MAX_MSG_PER_5MIN:
        return False, 300 - (now - history[0])
    history.append(now)
    st.session_state["voice_msg_times"] = history
    return True, 0


def main():
    if "user_id" not in st.session_state:
        st.warning("Please log in from the main page.")
        st.stop()

    db = get_session()
    user = get_user(db, st.session_state["user_id"])
    profile = ensure_profile(db, user.id)
    db.commit()

    page_header("💬 Your Voice", "A supportive, non‑clinical buddy that learns from your journal + missions.")

    if not is_onboarded(profile):
        st.info("Finish onboarding first on the **🏠 Dashboard**.")
        return

    card(
        "<b>Hi! I’m Your Voice 🐣</b><br>"
        "Tell me how your day is going, or ask for a tiny next step.<br>"
        "<span class='ss-muted'>I’m supportive, not a therapist. If you feel unsafe, reach out to a trusted adult or emergency services.</span>",
        panel=True
    )

    with st.expander("🧩 Safety & help resources", expanded=False):
        st.write(CRISIS_RESOURCES_TEXT)

    st.markdown("### Chat")
    convo = get_conversation(db, user.id, limit=50)
    st.markdown("<div class='ss-bubble-wrap'>", unsafe_allow_html=True)
    for msg in convo:
        bubble(msg.role, msg.text)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Send a message")
    user_text = st.text_area("Type here (keep it kind 💛)", placeholder="Example: I kept procrastinating today…", height=90)

    col1, col2 = st.columns([0.75, 0.25])
    with col1:
        send = st.button("Send ✨", type="primary")
    with col2:
        clear = st.button("Clear input")

    if clear:
        st.rerun()

    if send:
        ok, wait_s = _rate_limit_ok()
        if not ok:
            st.warning(f"Slow down a bit 🌼 Try again in ~{int(wait_s)} seconds.")
        elif not user_text.strip():
            st.info("Type something first ✍️")
        else:
            _ = chat_once(db, user.id, user_text.strip())
            db.commit()
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Memory (what I can reference)")
    st.caption("This is stored in your database. You can delete items any time.")

    mems = list_memory(db, user.id, limit=30)
    if not mems:
        st.info("No memory yet. Add a journal entry 📓 to build helpful context!")
    else:
        for m in mems:
            card(
                f"<b>#{m.id}</b> <span class='ss-badge'>{m.kind}</span><br>"
                f"{m.content}<br><span class='ss-muted'>{m.created_at}</span>"
            )
            if st.button(f"Delete memory #{m.id}", key=f"delmem_{m.id}"):
                delete_memory_item(db, user.id, m.id)
                db.commit()
                st.toast("Deleted ✅", icon="🗑️")
                st.rerun()

main()
EOT

# 7) tests/test_voice_integration.py
cat > tests/test_voice_integration.py <<'EOT'
from soulsync.models import VoiceMessage, Profile
from soulsync.services.voice import chat_once


def test_voice_chat_fallback_saves_messages(db_session, test_user):
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one_or_none()
    if not prof:
        prof = Profile(user_id=test_user.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}')
        db_session.add(prof)
        db_session.commit()

    res = chat_once(db_session, test_user.id, "I feel stuck with homework.")
    db_session.commit()

    assert res["assistant"]

    msgs = db_session.query(VoiceMessage).filter_by(user_id=test_user.id).order_by(VoiceMessage.created_at.asc()).all()
    assert len(msgs) >= 2
    assert msgs[-2].role == "user"
    assert msgs[-1].role == "assistant"


def test_voice_moderation_blocks_toxic(db_session, test_user):
    res = chat_once(db_session, test_user.id, "You are stupid")
    db_session.commit()
    assert res["flagged"] is True
EOT


echo "✅ Module 5 generated/updated successfully."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 5: Your Voice RAG + moderation + journal\""
echo "  git push"
echo "Optional:"
echo "  pytest -q"
