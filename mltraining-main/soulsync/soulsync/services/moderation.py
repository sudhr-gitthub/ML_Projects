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
