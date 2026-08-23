"""Deterministic Boutiqaat entity detection and normalization."""

import re
import unicodedata

BOUTIQAAT_VARIANTS = [
    "boutiqaat",
    "boutiqaat.com",
    "boutiqaat com",
    "بوتيكات",
    "boutiqat",
]

RECOMMENDATION_PATTERNS = [
    r"\brecommend(?:ed|s|ation)?\b",
    r"\bbest\b",
    r"\btop\b",
    r"\btry\b",
    r"\bshop at\b",
    r"\bbuy from\b",
    r"\bconsider\b",
    r"\bgreat option\b",
    r"\bpopular choice\b",
    r"\bleading\b",
]

MENTION_ONLY_PATTERNS = [
    r"\bsuch as\b",
    r"\bincluding\b",
    r"\balong with\b",
    r"\bas well as\b",
    r"\bcompared to\b",
    r"\bvs\.?\b",
    r"\bversus\b",
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.lower())
    text = re.sub(r"https?://(www\.)?", "", text)
    text = re.sub(r"[^\w\s\u0600-\u06FF.]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def contains_boutiqaat(text: str) -> bool:
    normalized = normalize_text(text)
    return any(v in normalized for v in BOUTIQAAT_VARIANTS)


def _sentence_context(text: str, variant: str) -> str:
    normalized = normalize_text(text)
    idx = normalized.find(variant)
    if idx == -1:
        return normalized
    start = max(0, idx - 120)
    end = min(len(normalized), idx + len(variant) + 120)
    return normalized[start:end]


def is_boutiqaat_recommended(answer_text: str, structured_recommended: bool | None = None) -> bool:
    """
    Determine if Boutiqaat is recommended (not merely mentioned).

    Rules:
    1. If structured output explicitly marks recommended=True, trust it.
    2. If mentioned in a numbered/top list with recommendation language -> recommended.
    3. If mentioned with 'such as', 'including', 'vs' without purchase intent -> not recommended.
    """
    if not contains_boutiqaat(answer_text):
        return False

    if structured_recommended is True:
        return True
    if structured_recommended is False:
        return False

    normalized = normalize_text(answer_text)
    for variant in BOUTIQAAT_VARIANTS:
        if variant not in normalized:
            continue
        context = _sentence_context(answer_text, variant)

        for pattern in MENTION_ONLY_PATTERNS:
            if re.search(pattern, context):
                has_rec = any(re.search(p, context) for p in RECOMMENDATION_PATTERNS)
                if not has_rec:
                    return False

        for pattern in RECOMMENDATION_PATTERNS:
            if re.search(pattern, context):
                return True

        if re.search(rf"\d+\.\s*{re.escape(variant)}", normalized):
            return True

    return False


def extract_boutiqaat_position(recommendations: list[dict]) -> int | None:
    """Return position from structured recommendations list."""
    for rec in recommendations:
        company = normalize_text(rec.get("company", ""))
        if any(v in company for v in BOUTIQAAT_VARIANTS):
            if rec.get("recommended", True):
                return rec.get("position")
    return None
