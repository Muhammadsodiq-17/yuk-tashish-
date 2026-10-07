from fastapi import FastAPI
from database import get_connection
from fastapi import FastAPI, HTTPException
from schemas import RegisterRequest
from security import hash_password
from schemas import LoginRequest
from security import check_password
from security import create_token

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def helth_db():
    conn = get_connection()
    rows = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()
    son = rows[0]
    conn.close()
    return {"users": son}


@app.post("/auth/register")
def register(data: RegisterRequest):
    if data.rol not in ("client", "driver"):
        raise HTTPException(status_code=400, detail="Rol faqat client yoki driver bo'lishi mumkin")
    if len(data.parol) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 belgi bo'lsin")

    conn = get_connection()
    mavjud = conn.execute(
        "SELECT id FROM users WHERE telefon_raqam = ?", (data.telefon_raqam,)
    ).fetchone()
    if mavjud:
        conn.close()
        raise HTTPException(status_code=409, detail="Bu telefon raqam band")

    parol_hesh = hash_password(data.parol)
    cursor = conn.execute(
        "INSERT INTO users (ism, familya, telefon_raqam, parol_hesh, rol) VALUES (?, ?, ?, ?, ?)",
        (data.ism, data.familya, data.telefon_raqam, parol_hesh, data.rol),
    )
    conn.commit()
    yangi_id = cursor.lastrowid
    conn.close()
    return {"id": yangi_id, "ism": data.ism}


@app.post("/auth/login")
def login(data: LoginRequest):
    conn = get_connection()
    mavjud = conn.execute(
        "SELECT id, parol_hesh, rol FROM users WHERE telefon_raqam =?", (data.telefon_raqam,)).fetchone()
    conn.close()

    if not mavjud or not check_password(data.parol, mavjud["parol_hesh"]):
        raise HTTPException(status_code=401, detail="Telefon yoki parol noto'g'ri")
    return {"token": create_token(mavjud["id"], mavjud["rol"])}
