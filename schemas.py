from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    ism: str
    familya: str
    telefon_raqam: str
    parol: str
    rol: str


class LoginRequest(BaseModel):
    telefon_raqam: str
    parol: str


class CargoPostCreate(BaseModel):
    olish_manzili: str
    yetkazish_manzili: str
    yuk_turi: str
    ogirligi: float = Field(gt=0)
    taklifqilingan_narx: int = Field(gt=0)

