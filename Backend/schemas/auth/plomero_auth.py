from pydantic import BaseModel, EmailStr


# ─────────────────────────────
# LOGIN
# ─────────────────────────────
class PlomeroLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PlomeroLoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_plomero: int
    nombre: str


# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────
class OlvidePasswordPlomeroRequest(BaseModel):
    email: EmailStr


class ResetPasswordPlomeroRequest(BaseModel):
    token: str
    nueva_password: str