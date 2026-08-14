import base64, hashlib, hmac, json, time
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import JWT_EXPIRE_MINUTES, JWT_SECRET
from app.db import get_db
from app.models.simulation import User

bearer = HTTPBearer(auto_error=False)
def hash_password(password: str) -> str:
    salt = hashlib.sha256(f"{JWT_SECRET}:{password}".encode()).hexdigest()[:32]
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 240000).hex()}"
def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 240000).hex(), digest)
    except ValueError: return False
def _b64(data: bytes) -> str: return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
def create_access_token(user_id: int) -> str:
    header = _b64(b'{"alg":"HS256","typ":"JWT"}')
    payload = _b64(json.dumps({"sub": str(user_id), "exp": int(time.time()) + JWT_EXPIRE_MINUTES * 60}, separators=(",", ":")).encode())
    signing = f"{header}.{payload}"
    return f"{signing}.{_b64(hmac.new(JWT_SECRET.encode(), signing.encode(), hashlib.sha256).digest())}"
def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials or credentials.scheme.lower() != "bearer": raise HTTPException(401, "Authentication required")
    try:
        header, payload, signature = credentials.credentials.split(".")
        signing = f"{header}.{payload}"
        if not hmac.compare_digest(signature, _b64(hmac.new(JWT_SECRET.encode(), signing.encode(), hashlib.sha256).digest())): raise ValueError
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if int(data["exp"]) < time.time(): raise ValueError
        user = db.get(User, int(data["sub"]))
    except (ValueError, KeyError, json.JSONDecodeError, TypeError): user = None
    if not user: raise HTTPException(401, "Invalid or expired token")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Administrator permission required")
    return user
