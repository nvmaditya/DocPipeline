from __future__ import annotations

import re
import unicodedata

try:
    from ftfy import fix_text as _fix_text
except ImportError:
    def _fix_text(text: str) -> str:
        return text

_CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_MULTI_WS_RE = re.compile(r"[ \t]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_HYPHEN_BREAK_RE = re.compile(r"(\w)-\n(\w)")


def clean_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    fixed = _fix_text(normalized)
    no_control = _CONTROL_RE.sub("", fixed)
    rejoined = _HYPHEN_BREAK_RE.sub(r"\1\2", no_control)
    ws_collapsed = _MULTI_WS_RE.sub(" ", rejoined)
    nl_collapsed = _MULTI_NL_RE.sub("\n\n", ws_collapsed)
    return nl_collapsed.strip()
