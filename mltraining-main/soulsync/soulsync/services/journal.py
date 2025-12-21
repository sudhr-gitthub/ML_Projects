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
