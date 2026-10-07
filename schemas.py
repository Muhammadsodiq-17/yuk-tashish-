from pydantic import BaseModel


class RegisterRequest(BaseModel):
    ism: str
    familya: str
    telefon_raqam: str
    parol: str
    rol: str
class LoginRequest(BaseModel):
    telefon_raqam: str
    parol:str
