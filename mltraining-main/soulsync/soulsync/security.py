import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email.strip().lower()))

def valid_handle(handle: str) -> bool:
    if not handle:
        return False
    h = handle.strip()
    if len(h) < 3 or len(h) > 32:
        return False
    return re.match(r"^[a-zA-Z0-9_]+$", h) is not None
