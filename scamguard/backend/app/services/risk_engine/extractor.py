import re

URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+|\b[\w-]+\.(?:com|net|org|cm|xyz|top|info|tk|online|site|shop)(?:/[^\s]*)?")
PHONE_PATTERN = re.compile(r"(?:\+?237)?\s?[62]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}")
SHORTCODE_PATTERN = re.compile(r"\b\d{3,5}\b")
AMOUNT_PATTERN = re.compile(r"\b\d[\d\s.]{2,}\s?(?:fcfa|f cfa|francs?|xaf)\b", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    return list(dict.fromkeys(URL_PATTERN.findall(text)))


def extract_phones(text: str) -> list[str]:
    found = PHONE_PATTERN.findall(text)
    return list(dict.fromkeys(normalize_phone(number) for number in found))


def extract_amounts(text: str) -> list[str]:
    return [match.strip() for match in AMOUNT_PATTERN.findall(text)]


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("237"):
        return f"+{digits}"
    return f"+237{digits.lstrip('0')}"
