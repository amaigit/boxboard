from fastapi import FastAPI, Depends, HTTPException, status, Body
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

class UserCreate(BaseModel):
    nome: str
    email: str
    ruolo: str = "Operatore"
    password: str

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    ruolo: Optional[str] = None
    password: Optional[str] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

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

# --- ENDPOINT CRUD UTENTI ---
@app.get("/utenti", response_model=list[UserOut], tags=["Utenti"])
def list_utenti(admin: Utente = Depends(require_admin)):
    with get_session() as session:
        utenti = session.query(Utente).all()
        return [UserOut(id=u.id, nome=u.nome, email=u.email, ruolo=u.ruolo) for u in utenti]

@app.get("/utenti/{utente_id}", response_model=UserOut, tags=["Utenti"])
def get_utente(utente_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        u = session.get(Utente, utente_id)
        if not u:
            raise HTTPException(404, "Utente non trovato")
        return UserOut(id=u.id, nome=u.nome, email=u.email, ruolo=u.ruolo)

@app.post("/utenti", response_model=UserOut, tags=["Utenti"])
def create_utente(user: UserCreate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        if session.query(Utente).filter(Utente.email == user.email).first():
            raise HTTPException(400, "Email già registrata")
        hashed = get_password_hash(user.password)
        nuovo = Utente(nome=user.nome, email=user.email, ruolo=user.ruolo, password=hashed)
        session.add(nuovo)
        session.commit()
        return UserOut(id=nuovo.id, nome=nuovo.nome, email=nuovo.email, ruolo=nuovo.ruolo)

@app.put("/utenti/{utente_id}", response_model=UserOut, tags=["Utenti"])
def update_utente_api(utente_id: int, user: UserUpdate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        u = session.get(Utente, utente_id)
        if not u:
            raise HTTPException(404, "Utente non trovato")
        if user.nome is not None:
            u.nome = user.nome
        if user.email is not None:
            u.email = user.email
        if user.ruolo is not None:
            u.ruolo = user.ruolo
        if user.password is not None:
            u.password = get_password_hash(user.password)
        session.commit()
        return UserOut(id=u.id, nome=u.nome, email=u.email, ruolo=u.ruolo)

@app.delete("/utenti/{utente_id}", tags=["Utenti"])
def delete_utente_api(utente_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        u = session.get(Utente, utente_id)
        if not u:
            raise HTTPException(404, "Utente non trovato")
        session.delete(u)
        session.commit()
        return {"detail": "Utente eliminato"}

# --- CAMBIO PASSWORD PERSONALE ---
@app.post("/me/change-password", tags=["Auth"])
def change_password(data: ChangePassword, current_user: Utente = Depends(get_current_user)):
    if current_user.password:
        valid = verify_password(data.old_password, current_user.password)
    else:
        import hashlib
        valid = data.old_password == hashlib.sha256(current_user.email.encode()).hexdigest()
    if not valid:
        raise HTTPException(400, "Vecchia password errata")
    with get_session() as session:
        u = session.get(Utente, current_user.id)
        u.password = get_password_hash(data.new_password)
        session.commit()
    return {"detail": "Password aggiornata"}

# --- AGGIORNA PROFILO PERSONALE ---
@app.put("/me", response_model=UserOut, tags=["Auth"])
def update_me(user: UserUpdate, current_user: Utente = Depends(get_current_user)):
    with get_session() as session:
        u = session.get(Utente, current_user.id)
        if user.nome is not None:
            u.nome = user.nome
        if user.email is not None:
            u.email = user.email
        session.commit()
        return UserOut(id=u.id, nome=u.nome, email=u.email, ruolo=u.ruolo)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 