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
