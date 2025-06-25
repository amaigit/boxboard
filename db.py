from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import config

Base = declarative_base()

# Costruzione della stringa di connessione in base al tipo di DB
if config.DB_TYPE == 'mariadb' or config.DB_TYPE == 'mysql':
    DB_URL = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
elif config.DB_TYPE == 'postgresql':
    DB_URL = f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
elif config.DB_TYPE == 'sqlite':
    DB_URL = f"sqlite:///{config.DB_NAME}.db"
else:
    raise ValueError(f"Tipo di database non supportato: {config.DB_TYPE}")

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    """Restituisce una nuova sessione SQLAlchemy"""
    return SessionLocal() 