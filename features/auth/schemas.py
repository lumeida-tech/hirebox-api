import re
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator


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

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de l'entreprise ne peut pas être vide")
        if len(v.strip()) < 2:
            raise ValueError("Le nom de l'entreprise doit contenir au moins 2 caractères")
        return v.strip()

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("L'URL du site web ne peut pas être vide")
        if not v.startswith(("http://", "https://")):
            raise ValueError("L'URL du site web doit commencer par http:// ou https://")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 10:
            errors.append("au moins 10 caractères")
        if not re.search(r"[a-zA-Z]", v):
            errors.append("au moins une lettre")
        if not re.search(r"\d", v):
            errors.append("au moins un chiffre")
        if not re.search(r"[^a-zA-Z0-9]", v):
            errors.append("au moins un caractère spécial (!@#$%...)")
        if errors:
            raise ValueError(f"Le mot de passe doit contenir : {', '.join(errors)}")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("L'email ne peut pas être vide")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le mot de passe ne peut pas être vide")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    password_strength: PasswordStrength | None = None


class RefreshRequest(BaseModel):
    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le refresh token ne peut pas être vide")
        return v.strip()


class RegisterResponse(BaseModel):
    id: str
    email: str
    company_name: str
    website: str
    role: str
    is_active: bool
    password_strength: PasswordStrength
    message: str


class ActivateRequest(BaseModel):
    token: str

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le token d'activation ne peut pas être vide")
        return v.strip()


class UserResponse(BaseModel):
    id: str
    email: str
    company_name: str
    website: str
    role: str
    is_active: bool