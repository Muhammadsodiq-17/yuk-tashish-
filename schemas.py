from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    mijoz_id: str
    ism: str
    familya: str
    telefon_raqam: str
    parol: str
    rol: str


class LoginRequest(BaseModel):
    mijoz_id: str
    telefon_raqam: str
    parol: str


class CargoPostCreate(BaseModel):
    olish_manzili: str
    yetkazish_manzili: str
    yuk_turi: str
    ogirligi: float
    taklifqilingan_narx: int = Field(gt=0)
    ogirligi: float = Field(gt=0)
