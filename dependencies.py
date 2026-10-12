from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from security import decode_token

bearer = HTTPBearer()


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
        creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    try:
        payload = decode_token(creds.credentials)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token muddati tugagan")
    except jwt.InvalidTokenError:
        raise _unauthorized("Token noto'g'ri")

    user_id = payload.get("user_id")
    rol = payload.get("rol")
    if user_id is None or rol is None:
        raise _unauthorized("Token noto'g'ri")

    return {"id": user_id, "rol": rol}


def require_role(*ruxsat_etilgan_rollar: str):
    def tekshiruvchi(user: dict = Depends(get_current_user)) -> dict:
        if user["rol"] not in ruxsat_etilgan_rollar:
            raise HTTPException(
                status_code=403,
                detail="Bu amal uchun ruxsat yo'q",
            )
        return user

    return tekshiruvchi
