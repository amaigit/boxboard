from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Boolean,
    Date,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from sqlalchemy import Enum as SqlEnum
import config

Base = declarative_base()

try:
    if config.DB_TYPE == "mariadb" or config.DB_TYPE == "mysql":
        DB_URL = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    elif config.DB_TYPE == "postgresql":
        DB_URL = f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    elif config.DB_TYPE == "sqlite":
        DB_URL = f"sqlite:///{config.DB_NAME}.db"
    else:
        raise ValueError(f"Tipo di database non supportato: {config.DB_TYPE}")
    engine = create_engine(DB_URL, echo=False, future=True)
    # Test connessione immediata
    with engine.connect() as conn:
        conn.execute("SELECT 1")
except Exception as e:
    if getattr(config, "DB_FALLBACK_TO_SQLITE", False):
        print(f"[WARN] Connessione al DB fallita ({e}), passo a SQLite locale!")
        DB_URL = f"sqlite:///boxboard.db"
        engine = create_engine(DB_URL, echo=False, future=True)
    else:
        raise
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Restituisce una nuova sessione SQLAlchemy"""
    return SessionLocal()


def test_db_connection():
    """Crea le tabelle e testa la connessione al database configurato."""
    try:
        Base.metadata.create_all(engine)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"Connessione e creazione tabelle riuscita su {config.DB_TYPE}!")
    except Exception as e:
        print(f"Errore di connessione o creazione tabelle: {e}")


class Utente(Base):
    __tablename__ = "utenti"
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    ruolo = Column(
        SqlEnum(
            "Operatore", "Coordinatore", "Altro", name="ruolo_enum", native_enum=False
        ),
        default="Operatore",
    )
    email = Column(String(255), unique=True)
    # relazioni
    note = relationship("Nota", back_populates="autore")
    oggetto_attivita = relationship("OggettoAttivita", back_populates="utente")


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    indirizzo = Column(Text)
    note = Column(Text)
    data_creazione = Column(DateTime, default=datetime.utcnow)
    # relazioni
    oggetti = relationship("Oggetto", back_populates="location")
    note_rel = relationship("Nota", back_populates="location")


class Oggetto(Base):
    __tablename__ = "oggetti"
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    stato = Column(
        SqlEnum(
            "da_rimuovere",
            "smaltito",
            "venduto",
            "in_attesa",
            "completato",
            name="stato_enum",
            native_enum=False,
        ),
        default="da_rimuovere",
    )
    tipo = Column(
        SqlEnum("oggetto", "contenitore", name="tipo_enum", native_enum=False),
        default="oggetto",
    )
    location_id = Column(Integer, ForeignKey("locations.id"))
    contenitore_id = Column(Integer, ForeignKey("oggetti.id"))
    data_rilevamento = Column(DateTime, default=datetime.utcnow)
    # relazioni
    location = relationship("Location", back_populates="oggetti")
    contenitore = relationship("Oggetto", remote_side=[id])
    attivita = relationship("OggettoAttivita", back_populates="oggetto")
    note = relationship("Nota", back_populates="oggetto")


class Attivita(Base):
    __tablename__ = "attivita"
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    # relazioni
    oggetto_attivita = relationship("OggettoAttivita", back_populates="attivita")
    note = relationship("Nota", back_populates="attivita")


class OggettoAttivita(Base):
    __tablename__ = "oggetto_attivita"
    id = Column(Integer, primary_key=True)
    oggetto_id = Column(Integer, ForeignKey("oggetti.id"), nullable=False)
    attivita_id = Column(Integer, ForeignKey("attivita.id"), nullable=False)
    completata = Column(Boolean, default=False)
    data_prevista = Column(Date)
    data_completamento = Column(Date)
    assegnato_a = Column(Integer, ForeignKey("utenti.id"))
    # relazioni
    oggetto = relationship("Oggetto", back_populates="attivita")
    attivita = relationship("Attivita", back_populates="oggetto_attivita")
    utente = relationship("Utente", back_populates="oggetto_attivita")


class Nota(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    testo = Column(Text, nullable=False)
    oggetto_id = Column(Integer, ForeignKey("oggetti.id"))
    attivita_id = Column(Integer, ForeignKey("attivita.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    autore_id = Column(Integer, ForeignKey("utenti.id"))
    data = Column(DateTime, default=datetime.utcnow)
    # relazioni
    oggetto = relationship("Oggetto", back_populates="note")
    attivita = relationship("Attivita", back_populates="note")
    location = relationship("Location", back_populates="note_rel")
    autore = relationship("Utente", back_populates="note")


class LogOperazione(Base):
    __tablename__ = "log_operazioni"
    id = Column(Integer, primary_key=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=False)
    azione = Column(String(50), nullable=False)  # es: 'create', 'update', 'delete'
    entita = Column(String(50), nullable=False)  # es: 'oggetto', 'utente', ...
    entita_id = Column(Integer, nullable=True)
    dettagli = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    utente = relationship("Utente")
