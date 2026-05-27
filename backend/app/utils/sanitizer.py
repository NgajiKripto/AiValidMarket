import re


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """Sanitize user input by removing control characters and enforcing max length.

    Keeps newlines and tabs. Removes null bytes.
    """
    if not isinstance(text, str):
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Remove control characters except newline (\n), carriage return (\r), and tab (\t)
    text = re.sub(r"[^\x09\x0a\x0d\x20-\x7e\x80-\uffff]", "", text)
    # Enforce max length
    return text[:max_length]


def sanitize_log_input(text: str, max_length: int = 200) -> str:
    """Sanitize text for log output to prevent log injection.

    Replaces newlines/carriage returns with spaces, strips control chars,
    and truncates to max_length.
    """
    if not isinstance(text, str):
        return ""
    # Replace newlines and carriage returns with spaces
    text = text.replace("\n", " ").replace("\r", " ")
    # Remove null bytes
    text = text.replace("\x00", "")
    # Remove other control characters (keep printable + space + tab)
    text = re.sub(r"[^\x09\x20-\x7e\x80-\uffff]", "", text)
    # Truncate
    return text[:max_length]


def validate_chat_history(chat_history: list) -> list:
    """Validate and filter chat history to only allow safe roles and content.

    Only allows entries with role in ('user', 'assistant') and content that
    is a non-empty string.
    """
    if not isinstance(chat_history, list):
        return []
    allowed_roles = ("user", "assistant")
    cleaned = []
    for entry in chat_history:
        if not isinstance(entry, dict):
            continue
        role = entry.get("role")
        content = entry.get("content")
        if role in allowed_roles and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content})
    return cleaned


def scan_content_for_injection(content: str) -> tuple:
    """Check content for common prompt injection patterns.

    Returns (is_safe, reason) tuple. is_safe is True if no injection detected.
    """
    if not isinstance(content, str):
        return (True, "")

    patterns = [
        (r"ignore\s+(all\s+)?previous\s+instructions", "ignore previous instructions pattern"),
        (r"disregard\s+(all\s+)?(previous|above|prior)", "disregard instructions pattern"),
        (r"you\s+are\s+now\s+", "role reassignment pattern"),
        (r"new\s+instructions?\s*:", "new instructions pattern"),
        (r"system\s*prompt\s*:", "system prompt override pattern"),
        (r"forget\s+(everything|all|previous)", "forget instructions pattern"),
        (r"\[INST\]", "instruction tag injection"),
        (r"<\|im_start\|>", "chat markup injection"),
    ]

    content_lower = content.lower()
    for pattern, reason in patterns:
        if re.search(pattern, content_lower):
            return (False, reason)

    return (True, "")
