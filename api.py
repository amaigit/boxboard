from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from db import get_session, Utente, Location, Oggetto, Attivita, Nota, LogOperazione
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

class LocationOut(BaseModel):
    id: int
    nome: str
    indirizzo: Optional[str] = None
    note: Optional[str] = None
    data_creazione: datetime
    class Config:
        orm_mode = True

class LocationCreate(BaseModel):
    nome: str
    indirizzo: Optional[str] = None
    note: Optional[str] = None

class LocationUpdate(BaseModel):
    nome: Optional[str] = None
    indirizzo: Optional[str] = None
    note: Optional[str] = None

class OggettoOut(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str] = None
    stato: str
    tipo: str
    location_id: Optional[int] = None
    contenitore_id: Optional[int] = None
    data_rilevamento: datetime
    class Config:
        orm_mode = True

class OggettoCreate(BaseModel):
    nome: str
    descrizione: Optional[str] = None
    stato: Optional[str] = None
    tipo: Optional[str] = None
    location_id: Optional[int] = None
    contenitore_id: Optional[int] = None
    data_rilevamento: Optional[datetime] = None

class OggettoUpdate(BaseModel):
    nome: Optional[str] = None
    descrizione: Optional[str] = None
    stato: Optional[str] = None
    tipo: Optional[str] = None
    location_id: Optional[int] = None
    contenitore_id: Optional[int] = None
    data_rilevamento: Optional[datetime] = None

class AttivitaOut(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str] = None
    class Config:
        orm_mode = True

class AttivitaCreate(BaseModel):
    nome: str
    descrizione: Optional[str] = None

class AttivitaUpdate(BaseModel):
    nome: Optional[str] = None
    descrizione: Optional[str] = None

class NotaOut(BaseModel):
    id: int
    testo: str
    oggetto_id: Optional[int] = None
    attivita_id: Optional[int] = None
    location_id: Optional[int] = None
    autore_id: Optional[int] = None
    data: datetime
    class Config:
        orm_mode = True

class NotaCreate(BaseModel):
    testo: str
    oggetto_id: Optional[int] = None
    attivita_id: Optional[int] = None
    location_id: Optional[int] = None
    autore_id: Optional[int] = None
    data: Optional[datetime] = None

class NotaUpdate(BaseModel):
    testo: Optional[str] = None
    oggetto_id: Optional[int] = None
    attivita_id: Optional[int] = None
    location_id: Optional[int] = None
    autore_id: Optional[int] = None
    data: Optional[datetime] = None

class LogOperazioneOut(BaseModel):
    id: int
    utente_id: int
    azione: str
    entita: str
    entita_id: Optional[int] = None
    dettagli: Optional[str] = None
    timestamp: datetime
    class Config:
        orm_mode = True

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

# --- ENDPOINT CRUD LOCATION ---
@app.get("/locations", response_model=list[LocationOut], tags=["Location"])
def list_locations(user: Utente = Depends(get_current_user)):
    with get_session() as session:
        locations = session.query(Location).all()
        return locations

@app.get("/locations/{location_id}", response_model=LocationOut, tags=["Location"])
def get_location(location_id: int, user: Utente = Depends(get_current_user)):
    with get_session() as session:
        loc = session.get(Location, location_id)
        if not loc:
            raise HTTPException(404, "Location non trovata")
        return loc

@app.post("/locations", response_model=LocationOut, tags=["Location"])
def create_location(location: LocationCreate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        nuova = Location(
            nome=location.nome,
            indirizzo=location.indirizzo,
            note=location.note
        )
        session.add(nuova)
        session.commit()
        session.refresh(nuova)
        return nuova

@app.put("/locations/{location_id}", response_model=LocationOut, tags=["Location"])
def update_location(location_id: int, location: LocationUpdate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        loc = session.get(Location, location_id)
        if not loc:
            raise HTTPException(404, "Location non trovata")
        if location.nome is not None:
            loc.nome = location.nome
        if location.indirizzo is not None:
            loc.indirizzo = location.indirizzo
        if location.note is not None:
            loc.note = location.note
        session.commit()
        return loc

@app.delete("/locations/{location_id}", tags=["Location"])
def delete_location(location_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        loc = session.get(Location, location_id)
        if not loc:
            raise HTTPException(404, "Location non trovata")
        session.delete(loc)
        session.commit()
        return {"detail": "Location eliminata"}

# --- ENDPOINT CRUD OGGETTI ---
@app.get("/oggetti", response_model=list[OggettoOut], tags=["Oggetti"])
def list_oggetti(user: Utente = Depends(get_current_user)):
    with get_session() as session:
        oggetti = session.query(Oggetto).all()
        return oggetti

@app.get("/oggetti/{oggetto_id}", response_model=OggettoOut, tags=["Oggetti"])
def get_oggetto(oggetto_id: int, user: Utente = Depends(get_current_user)):
    with get_session() as session:
        obj = session.get(Oggetto, oggetto_id)
        if not obj:
            raise HTTPException(404, "Oggetto non trovato")
        return obj

@app.post("/oggetti", response_model=OggettoOut, tags=["Oggetti"])
def create_oggetto(oggetto: OggettoCreate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        nuovo = Oggetto(
            nome=oggetto.nome,
            descrizione=oggetto.descrizione,
            stato=oggetto.stato or 'da_rimuovere',
            tipo=oggetto.tipo or 'oggetto',
            location_id=oggetto.location_id,
            contenitore_id=oggetto.contenitore_id,
            data_rilevamento=oggetto.data_rilevamento or datetime.utcnow()
        )
        session.add(nuovo)
        session.commit()
        session.refresh(nuovo)
        return nuovo

@app.put("/oggetti/{oggetto_id}", response_model=OggettoOut, tags=["Oggetti"])
def update_oggetto(oggetto_id: int, oggetto: OggettoUpdate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        obj = session.get(Oggetto, oggetto_id)
        if not obj:
            raise HTTPException(404, "Oggetto non trovato")
        if oggetto.nome is not None:
            obj.nome = oggetto.nome
        if oggetto.descrizione is not None:
            obj.descrizione = oggetto.descrizione
        if oggetto.stato is not None:
            obj.stato = oggetto.stato
        if oggetto.tipo is not None:
            obj.tipo = oggetto.tipo
        if oggetto.location_id is not None:
            obj.location_id = oggetto.location_id
        if oggetto.contenitore_id is not None:
            obj.contenitore_id = oggetto.contenitore_id
        if oggetto.data_rilevamento is not None:
            obj.data_rilevamento = oggetto.data_rilevamento
        session.commit()
        return obj

@app.delete("/oggetti/{oggetto_id}", tags=["Oggetti"])
def delete_oggetto(oggetto_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        obj = session.get(Oggetto, oggetto_id)
        if not obj:
            raise HTTPException(404, "Oggetto non trovato")
        session.delete(obj)
        session.commit()
        return {"detail": "Oggetto eliminato"}

# --- ENDPOINT CRUD ATTIVITA ---
@app.get("/attivita", response_model=list[AttivitaOut], tags=["Attivita"])
def list_attivita(user: Utente = Depends(get_current_user)):
    with get_session() as session:
        attivita = session.query(Attivita).all()
        return attivita

@app.get("/attivita/{attivita_id}", response_model=AttivitaOut, tags=["Attivita"])
def get_attivita(attivita_id: int, user: Utente = Depends(get_current_user)):
    with get_session() as session:
        att = session.get(Attivita, attivita_id)
        if not att:
            raise HTTPException(404, "Attività non trovata")
        return att

@app.post("/attivita", response_model=AttivitaOut, tags=["Attivita"])
def create_attivita(attivita: AttivitaCreate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        nuova = Attivita(
            nome=attivita.nome,
            descrizione=attivita.descrizione
        )
        session.add(nuova)
        session.commit()
        session.refresh(nuova)
        return nuova

@app.put("/attivita/{attivita_id}", response_model=AttivitaOut, tags=["Attivita"])
def update_attivita(attivita_id: int, attivita: AttivitaUpdate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        att = session.get(Attivita, attivita_id)
        if not att:
            raise HTTPException(404, "Attività non trovata")
        if attivita.nome is not None:
            att.nome = attivita.nome
        if attivita.descrizione is not None:
            att.descrizione = attivita.descrizione
        session.commit()
        return att

@app.delete("/attivita/{attivita_id}", tags=["Attivita"])
def delete_attivita(attivita_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        att = session.get(Attivita, attivita_id)
        if not att:
            raise HTTPException(404, "Attività non trovata")
        session.delete(att)
        session.commit()
        return {"detail": "Attività eliminata"}

# --- ENDPOINT CRUD NOTE ---
@app.get("/note", response_model=list[NotaOut], tags=["Note"])
def list_note(user: Utente = Depends(get_current_user)):
    with get_session() as session:
        note = session.query(Nota).all()
        return note

@app.get("/note/{nota_id}", response_model=NotaOut, tags=["Note"])
def get_nota(nota_id: int, user: Utente = Depends(get_current_user)):
    with get_session() as session:
        n = session.get(Nota, nota_id)
        if not n:
            raise HTTPException(404, "Nota non trovata")
        return n

@app.post("/note", response_model=NotaOut, tags=["Note"])
def create_nota(nota: NotaCreate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        nuova = Nota(
            testo=nota.testo,
            oggetto_id=nota.oggetto_id,
            attivita_id=nota.attivita_id,
            location_id=nota.location_id,
            autore_id=nota.autore_id,
            data=nota.data or datetime.utcnow()
        )
        session.add(nuova)
        session.commit()
        session.refresh(nuova)
        return nuova

@app.put("/note/{nota_id}", response_model=NotaOut, tags=["Note"])
def update_nota(nota_id: int, nota: NotaUpdate, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        n = session.get(Nota, nota_id)
        if not n:
            raise HTTPException(404, "Nota non trovata")
        if nota.testo is not None:
            n.testo = nota.testo
        if nota.oggetto_id is not None:
            n.oggetto_id = nota.oggetto_id
        if nota.attivita_id is not None:
            n.attivita_id = nota.attivita_id
        if nota.location_id is not None:
            n.location_id = nota.location_id
        if nota.autore_id is not None:
            n.autore_id = nota.autore_id
        if nota.data is not None:
            n.data = nota.data
        session.commit()
        return n

@app.delete("/note/{nota_id}", tags=["Note"])
def delete_nota(nota_id: int, admin: Utente = Depends(require_admin)):
    with get_session() as session:
        n = session.get(Nota, nota_id)
        if not n:
            raise HTTPException(404, "Nota non trovata")
        session.delete(n)
        session.commit()
        return {"detail": "Nota eliminata"}

# --- ENDPOINT LOG OPERAZIONI (SOLO ADMIN) ---
@app.get("/log-operazioni", response_model=list[LogOperazioneOut], tags=["Log"])
def list_log_operazioni(admin: Utente = Depends(require_admin)):
    with get_session() as session:
        logs = session.query(LogOperazione).order_by(LogOperazione.timestamp.desc()).all()
        return logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 