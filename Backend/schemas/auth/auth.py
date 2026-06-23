from pydantic import BaseModel, EmailStr


# ─────────────────────────────
# LOGIN
# ─────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    id: int
    nombre: str
    rol: str


# ─────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────
class OlvidePasswordRequest(BaseModel):
    email: EmailStr


# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────
class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str