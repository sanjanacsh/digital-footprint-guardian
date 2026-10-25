"""Pattern-based detection and redaction for text."""
import re
from collections import Counter

PATTERNS = [
    ("Email address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), 25, "Medium"),
    ("Phone number", re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"), 20, "Medium"),
    ("API key / token", re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,}|AIza[0-9A-Za-z_-]{20,})\b"), 40, "High"),
    ("Password-like assignment", re.compile(r"(?i)\b(password|passwd|pwd|secret|api_key|token)\b\s*[:=]\s*['\"]?[^'\"\s,;]{4,}"), 40, "High"),
    ("IPv4 address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"), 10, "Low"),
]

def scan_text(text: str) -> dict:
    """Find supported sensitive patterns and calculate a simple capped risk score."""
    findings = []
    score = 0
    for label, pattern, points, risk in PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            findings.append({"type": label, "count": len(matches), "risk": risk})
            score += points * min(len(matches), 3)
    score = min(score, 100)
    level = "Low" if score < 25 else "Moderate" if score < 60 else "High"
    return {"score": score, "level": level, "findings": findings}

def redact_text(text: str) -> str:
    """Replace matches with labels while preserving the surrounding text."""
    result = text
    for label, pattern, _, _ in PATTERNS:
        result = pattern.sub(f"[REDACTED: {label}]", result)
    return result
