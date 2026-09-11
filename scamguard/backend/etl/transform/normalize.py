import hashlib
import re
import unicodedata

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+|\b[\w-]+\.(?:com|net|org|cm|xyz|top|info)\b")
WHITESPACE_PATTERN = re.compile(r"\s+")

FRENCH_MARKERS = {"le", "la", "les", "vous", "votre", "pour", "avec", "est", "une", "compte"}
ENGLISH_MARKERS = {"the", "your", "you", "please", "account", "click", "have", "won"}


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def clean_text(text: str) -> str:
    lowered = strip_accents(text.strip().lower())
    return WHITESPACE_PATTERN.sub(" ", lowered)


def mask_urls(text: str) -> str:
    return URL_PATTERN.sub("[URL]", text)


def count_urls(text: str) -> int:
    return len(URL_PATTERN.findall(text))


def content_hash(text: str) -> str:
    return hashlib.sha256(clean_text(text).encode()).hexdigest()


def detect_language(text: str) -> str:
    words = set(clean_text(text).split())
    french = len(words & FRENCH_MARKERS)
    english = len(words & ENGLISH_MARKERS)
    if french > english:
        return "fr"
    if english > french:
        return "en"
    return "mix"
