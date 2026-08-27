import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import (
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)
from app.db import get_db
from app.models.simulation import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
def google_login():
    if not GOOGLE_CLIENT_ID: raise HTTPException(503, "Google OAuth is not configured")
    params = urlencode({"client_id": GOOGLE_CLIENT_ID, "redirect_uri": GOOGLE_REDIRECT_URI, "response_type":"code", "scope":"openid email profile"})
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET: raise HTTPException(503, "Google OAuth is not configured")
    body = urlencode({"code":code,"client_id":GOOGLE_CLIENT_ID,"client_secret":GOOGLE_CLIENT_SECRET,"redirect_uri":GOOGLE_REDIRECT_URI,"grant_type":"authorization_code"}).encode()
    with urlopen(Request("https://oauth2.googleapis.com/token", data=body, method="POST")) as response: tokens=json.loads(response.read())
    with urlopen(Request("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization":f"Bearer {tokens['access_token']}"})) as response: profile=json.loads(response.read())
    email = profile["email"].lower(); user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(external_id=email, email=email, password_hash="GOOGLE_OAUTH", google_id=profile.get("sub"), auth_provider="google", role="USER"); db.add(user); db.commit(); db.refresh(user)
    return RedirectResponse(f"{FRONTEND_URL}/?access_token={create_access_token(user.id)}")

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    email = str(request.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(external_id=email, email=email, password_hash=hash_password(request.password), role="USER")
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(request.email).lower()))
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
