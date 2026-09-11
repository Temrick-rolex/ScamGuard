import re

PHONE_PATTERN = re.compile(r"(?:\+?237)?\s?[62]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}")
LONG_DIGITS_PATTERN = re.compile(r"\b\d{6,}\b")
CODE_PATTERN = re.compile(
    r"\b(?:code|pin|otp|mot de passe|password)\s*[:=]?\s*\d{4,8}\b", re.IGNORECASE
)
SHORT_CODE_PATTERN = re.compile(r"\b\d{4,6}\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
ACCOUNT_PATTERN = re.compile(r"\b[A-Z]{2}\d{10,}\b")


def anonymize(text: str) -> str:
    cleaned = EMAIL_PATTERN.sub("[EMAIL]", text)
    cleaned = CODE_PATTERN.sub("[CODE]", cleaned)
    cleaned = PHONE_PATTERN.sub("[TEL]", cleaned)
    cleaned = ACCOUNT_PATTERN.sub("[COMPTE]", cleaned)
    cleaned = LONG_DIGITS_PATTERN.sub("[NUM]", cleaned)
    return SHORT_CODE_PATTERN.sub("[CODE]", cleaned)


def contains_personal_data(text: str) -> bool:
    return bool(
        PHONE_PATTERN.search(text)
        or EMAIL_PATTERN.search(text)
        or LONG_DIGITS_PATTERN.search(text)
    )
