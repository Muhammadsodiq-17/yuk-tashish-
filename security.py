import bcrypt
import jwt
import datetime




def hash_password(parol):
    parol_hesh = parol.encode("utf-8")
    hesh_parol = bcrypt.hashpw(parol_hesh, bcrypt.gensalt())
    return hesh_parol.decode("utf-8")


def check_password(parol, hash_matn):
    return bcrypt.checkpw(parol.encode("utf-8"), hash_matn.encode("utf-8"))


Kalit = "Suniy-intelekt-orqali-kodlarni-va-dasturlash-tillarini-o'rganish"


def create_token(user_id, rol):
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    malumot = {"user_id": user_id,
               "rol": rol,
               "exp":exp}
    return jwt.encode(malumot, Kalit, algorithm="HS256")
