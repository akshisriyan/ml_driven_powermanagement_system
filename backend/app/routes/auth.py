from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime
import sqlite3
import os

from ..utils.auth import (
    create_access_token,
    authenticate_user,
    hash_password,
    get_current_user,
    require_admin,
    _get_db_path,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str | None = "client"  # allow specifying admin manually (should be protected in production)


@router.post("/register", response_model=UserPublic)
async def register_user(payload: RegisterRequest):
    if payload.role not in ("client", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    # Ensure unique
    cur.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (payload.username, payload.email))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already registered")
    cur.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (payload.username, payload.email, hash_password(payload.password), payload.role or "client")
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return UserPublic(id=user_id, username=payload.username, email=payload.email, role=payload.role or "client")


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expires = timedelta(minutes=60)
    token = create_access_token({"sub": user["username"], "role": user["role"]}, expires)
    return TokenResponse(
        access_token=token,
        expires_in=int(expires.total_seconds()),
        user=UserPublic(
            id=user["id"], username=user["username"], email=user["email"], role=user["role"]
        ),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current=Depends(get_current_user)):
    return UserPublic(id=current["id"], username=current["username"], email=current["email"], role=current["role"])


@router.get("/admin-test")
async def admin_only(_: dict = Depends(require_admin)):
    return {"message": "You are an admin"}
