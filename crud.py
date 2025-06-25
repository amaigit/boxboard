from db import get_session, Utente, Location, Oggetto, Attivita, OggettoAttivita, Nota, LogOperazione
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def log_operazione(utente_id, azione, entita, entita_id=None, dettagli=None):
    with get_session() as session:
        log = LogOperazione(
            utente_id=utente_id,
            azione=azione,
            entita=entita,
            entita_id=entita_id,
            dettagli=dettagli,
        )
        session.add(log)
        session.commit()

def add_utente(nome, ruolo, email, current_user_id=None):
    try:
        with get_session() as session:
            utente = Utente(nome=nome, ruolo=ruolo, email=email)
            session.add(utente)
            session.commit()
            if current_user_id:
                log_operazione(
                    current_user_id,
                    "create",
                    "utente",
                    utente.id,
                    f"Aggiunto utente {nome} ({email}) con ruolo {ruolo}",
                )
            return utente
    except IntegrityError as e:
        print(f"Errore di integrità (utente): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (utente): {e}")
        return None

def add_location(nome, indirizzo, note):
    try:
        with get_session() as session:
            location = Location(nome=nome, indirizzo=indirizzo, note=note)
            session.add(location)
            session.commit()
            return location
    except IntegrityError as e:
        print(f"Errore di integrità (location): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (location): {e}")
        return None

def add_oggetto(nome, descrizione, stato, tipo, location_id, contenitore_id=None):
    try:
        with get_session() as session:
            oggetto = Oggetto(
                nome=nome,
                descrizione=descrizione,
                stato=stato,
                tipo=tipo,
                location_id=location_id,
                contenitore_id=contenitore_id,
            )
            session.add(oggetto)
            session.commit()
            return oggetto
    except IntegrityError as e:
        print(f"Errore di integrità (oggetto): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (oggetto): {e}")
        return None

def add_attivita(nome, descrizione):
    try:
        with get_session() as session:
            attivita = Attivita(nome=nome, descrizione=descrizione)
            session.add(attivita)
            session.commit()
            return attivita
    except IntegrityError as e:
        print(f"Errore di integrità (attivita): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (attivita): {e}")
        return None

def add_oggetto_attivita(oggetto_id, attivita_id, data_prevista, assegnato_a=None):
    try:
        with get_session() as session:
            oa = OggettoAttivita(
                oggetto_id=oggetto_id,
                attivita_id=attivita_id,
                data_prevista=data_prevista,
                assegnato_a=assegnato_a,
            )
            session.add(oa)
            session.commit()
            return oa
    except IntegrityError as e:
        print(f"Errore di integrità (oggetto_attivita): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (oggetto_attivita): {e}")
        return None

def add_nota(
    testo, oggetto_id=None, attivita_id=None, location_id=None, autore_id=None
):
    try:
        with get_session() as session:
            nota = Nota(
                testo=testo,
                oggetto_id=oggetto_id,
                attivita_id=attivita_id,
                location_id=location_id,
                autore_id=autore_id,
            )
            session.add(nota)
            session.commit()
            return nota
    except IntegrityError as e:
        print(f"Errore di integrità (nota): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (nota): {e}")
        return None 