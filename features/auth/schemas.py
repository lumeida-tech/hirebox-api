import re
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator, HttpUrl


class PasswordStrength(str, Enum):
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


def evaluate_password(password: str) -> PasswordStrength:
    has_letter = bool(re.search(r"[a-zA-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", password))
    length = len(password)

    score = sum([has_letter, has_digit, has_special])

    if length >= 14 and score == 3:
        return PasswordStrength.STRONG
    elif length >= 10 and score >= 2:
        return PasswordStrength.MEDIUM
    else:
        return PasswordStrength.WEAK


class RegisterRequest(BaseModel):
    company_name: str
    website: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Le mot de passe doit contenir au moins 10 caractères")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Le mot de passe doit contenir au moins un caractère spécial")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    password_strength: PasswordStrength | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    company_name: str
    website: str
    role: str