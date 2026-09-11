from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import AccountStatus, Role


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if value.isalpha() or value.isdigit():
            raise ValueError("Le mot de passe doit melanger lettres et chiffres")
        return value

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        digits = value.replace(" ", "").replace("-", "")
        if not digits.startswith("+"):
            digits = f"+237{digits.lstrip('0')}"
        return digits


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserPublic(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: Role
    status: AccountStatus
    is_premium: bool

    model_config = {"from_attributes": True}


class DeviceSettingsPublic(BaseModel):
    sms_protection: bool
    call_alert: bool
    notifications: bool

    model_config = {"from_attributes": True}


class DeviceSettingsUpdate(BaseModel):
    sms_protection: bool | None = None
    call_alert: bool | None = None
    notifications: bool | None = None
