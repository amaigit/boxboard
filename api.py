from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from db import get_session, Utente
import os

# --- CONFIG ---
SECRET_KEY = os.environ.get("API_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- FastAPI setup ---
app = FastAPI(title="BoxBoard API", version="1.0.0")

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- MODELLI ---
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserOut(BaseModel):
    id: int
    nome: str
    email: str
    ruolo: str

# --- UTILITY JWT ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str):
    with get_session() as session:
        return session.query(Utente).filter(Utente.email == email).first()

# --- AUTENTICAZIONE ---
@app.post("/login", response_model=Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Email o password non validi")
    # Per ora la password è hash(email) se non presente
    if user.password:
        valid = verify_password(form_data.password, user.password)
    else:
        import hashlib
        valid = form_data.password == hashlib.sha256(user.email.encode()).hexdigest()
    if not valid:
        raise HTTPException(status_code=400, detail="Email o password non validi")
    access_token = create_access_token(data={"sub": user.email, "ruolo": user.ruolo})
    return {"access_token": access_token, "token_type": "bearer"}

# --- DIPENDENZA: utente autenticato ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token non valido o scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

# --- DIPENDENZA: solo admin ---
def require_admin(user: Utente = Depends(get_current_user)):
    if user.ruolo != "Coordinatore":
        raise HTTPException(status_code=403, detail="Permesso negato: solo admin")
    return user

# --- ENDPOINT PROFILO ---
@app.get("/me", response_model=UserOut, tags=["Auth"])
def read_users_me(current_user: Utente = Depends(get_current_user)):
    return UserOut(id=current_user.id, nome=current_user.nome, email=current_user.email, ruolo=current_user.ruolo)

# --- Healthcheck ---
@app.get("/health", tags=["Health"])
def healthcheck():
    """Verifica che l'API sia attiva"""
    return JSONResponse(content={"status": "ok"})

# --- Qui verranno aggiunti gli endpoint CRUD ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 