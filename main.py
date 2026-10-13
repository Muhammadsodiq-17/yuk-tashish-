from fastapi import FastAPI
import sqlite3
from database import get_connection
from fastapi import FastAPI, HTTPException, Depends
from schemas import RegisterRequest, LoginRequest, CargoPostCreate, OfferCreate
from security import hash_password, check_password, create_token
from dependencies import get_current_user, require_role

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


@app.get("/users/me")
def read_me(user: dict = Depends(get_current_user)):
    return user


@app.get("/test/client")
def test_client(user: dict = Depends(require_role("client"))):
    return {"xabar": "Siz clientsiz", "user": user}


@app.get("/test/driver")
def test_driver(user: dict = Depends(require_role("driver"))):
    return {"xabar": "Siz driversiz", "user": user}


@app.post("/cargo-posts", status_code=201)
def create_cargo_post(
        data: CargoPostCreate,
        user: dict = Depends(require_role("client")),
):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO cargo_post "
        "(mijoz_id, olish_manzili, yetkazish_manzili, yuk_turi, ogirligi, taklifqilingan_narx) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            user["id"],
            data.olish_manzili,
            data.yetkazish_manzili,
            data.yuk_turi,
            data.ogirligi,
            data.taklifqilingan_narx,
        ),
    )
    conn.commit()
    yangi_id = cursor.lastrowid
    conn.close()
    return {"id": yangi_id}


@app.get("/cargo-posts")
def list_cargo_posts(
        olish: str | None = None,
        yetkazish: str | None = None,
        max_ogirlik: float | None = None,
        user: dict = Depends(require_role("driver")),
):
    shartlar = ["holati = 'open'"]
    qiymatlar = []

    if olish is not None:
        shartlar.append("olish_manzili LIKE ?")
        qiymatlar.append(f"%{olish}%")
    if yetkazish is not None:
        shartlar.append("yetkazish_manzili LIKE ?")
        qiymatlar.append(f"%{yetkazish}%")
    if max_ogirlik is not None:
        shartlar.append("ogirligi <= ?")
        qiymatlar.append(max_ogirlik)

    sql = (
            "SELECT id, olish_manzili, yetkazish_manzili, yuk_turi, ogirligi, "
            "taklifqilingan_narx, yaratilgan_vaqt FROM cargo_post WHERE "
            + " AND ".join(shartlar)
            + " ORDER BY id DESC"
    )

    conn = get_connection()
    rows = conn.execute(sql, qiymatlar).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/cargo-posts/{post_id}/offers", status_code=201)
def create_offer(
        post_id: int,
        data: OfferCreate,
        user: dict = Depends(require_role("driver")),
):
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    try:

        post = conn.execute(
            "SELECT holati FROM cargo_post WHERE id = ?", (post_id,)
        ).fetchone()
        if post is None:
            raise HTTPException(status_code=404, detail="E'lon topilmadi")
        if post[0] != "open":
            raise HTTPException(status_code=409, detail="E'lon endi ochiq emas")

        try:
            cur = conn.execute(
                "INSERT INTO offers (cargo_post_id, haydovchi_id, narx, izoh) "
                "VALUES (?, ?, ?, ?)",
                (post_id, user["id"], data.narx, data.izoh),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Siz bu e'longa allaqachon taklif yuborgansiz",
            )

        conn.commit()
        return {"id": cur.lastrowid}
    finally:
        conn.close()
