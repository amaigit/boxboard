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
            return utente.id
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
            return location.id
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
            return oggetto.id
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
            return attivita.id
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
            return oa.id
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
            return nota.id
    except IntegrityError as e:
        print(f"Errore di integrità (nota): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (nota): {e}")
        return None

def update_utente(utente_id, nome=None, ruolo=None, email=None, current_user_id=None):
    try:
        with get_session() as session:
            utente = session.get(Utente, utente_id)
            if not utente:
                print(f"Utente con id {utente_id} non trovato")
                return False
            cambiamenti = []
            if nome is not None and utente.nome != nome:
                cambiamenti.append(f"nome: {utente.nome} -> {nome}")
                utente.nome = nome
            if ruolo is not None and utente.ruolo != ruolo:
                cambiamenti.append(f"ruolo: {utente.ruolo} -> {ruolo}")
                utente.ruolo = ruolo
            if email is not None and utente.email != email:
                cambiamenti.append(f"email: {utente.email} -> {email}")
                utente.email = email
            session.commit()
            if current_user_id and cambiamenti:
                log_operazione(
                    current_user_id,
                    "update",
                    "utente",
                    utente_id,
                    f"Modifiche: {', '.join(cambiamenti)}"
                )
            return True
    except IntegrityError as e:
        print(f"Errore di integrità (update utente): {e}")
        return False
    except SQLAlchemyError as e:
        print(f"Errore database (update utente): {e}")
        return False

def delete_utente(utente_id, current_user_id=None):
    try:
        with get_session() as session:
            utente = session.get(Utente, utente_id)
            if not utente:
                print(f"Utente con id {utente_id} non trovato")
                return False
            session.delete(utente)
            session.commit()
            if current_user_id:
                log_operazione(
                    current_user_id,
                    "delete",
                    "utente",
                    utente_id,
                    f"Eliminato utente con id {utente_id}"
                )
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete utente): {e}")
        return False

def update_location(location_id, nome=None, indirizzo=None, note=None):
    try:
        with get_session() as session:
            location = session.get(Location, location_id)
            if not location:
                print(f"Location con id {location_id} non trovata")
                return False
            if nome is not None:
                location.nome = nome
            if indirizzo is not None:
                location.indirizzo = indirizzo
            if note is not None:
                location.note = note
            session.commit()
            return location_id
    except SQLAlchemyError as e:
        print(f"Errore database (update location): {e}")
        return False

def delete_location(location_id):
    try:
        with get_session() as session:
            location = session.get(Location, location_id)
            if not location:
                print(f"Location con id {location_id} non trovata")
                return False
            session.delete(location)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete location): {e}")
        return False

def update_oggetto(oggetto_id, nome=None, descrizione=None, stato=None, tipo=None, location_id=None, contenitore_id=None):
    try:
        with get_session() as session:
            oggetto = session.get(Oggetto, oggetto_id)
            if not oggetto:
                print(f"Oggetto con id {oggetto_id} non trovato")
                return False
            if nome is not None:
                oggetto.nome = nome
            if descrizione is not None:
                oggetto.descrizione = descrizione
            if stato is not None:
                oggetto.stato = stato
            if tipo is not None:
                oggetto.tipo = tipo
            if location_id is not None:
                oggetto.location_id = location_id
            if contenitore_id is not None:
                oggetto.contenitore_id = contenitore_id
            session.commit()
            return oggetto_id
    except SQLAlchemyError as e:
        print(f"Errore database (update oggetto): {e}")
        return False

def delete_oggetto(oggetto_id):
    try:
        with get_session() as session:
            oggetto = session.get(Oggetto, oggetto_id)
            if not oggetto:
                print(f"Oggetto con id {oggetto_id} non trovato")
                return False
            session.delete(oggetto)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete oggetto): {e}")
        return False

def update_attivita(attivita_id, nome=None, descrizione=None):
    try:
        with get_session() as session:
            attivita = session.get(Attivita, attivita_id)
            if not attivita:
                print(f"Attività con id {attivita_id} non trovata")
                return False
            if nome is not None:
                attivita.nome = nome
            if descrizione is not None:
                attivita.descrizione = descrizione
            session.commit()
            return attivita_id
    except SQLAlchemyError as e:
        print(f"Errore database (update attivita): {e}")
        return False

def delete_attivita(attivita_id):
    try:
        with get_session() as session:
            attivita = session.get(Attivita, attivita_id)
            if not attivita:
                print(f"Attività con id {attivita_id} non trovata")
                return False
            session.delete(attivita)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete attivita): {e}")
        return False

def update_oggetto_attivita(oa_id, completata=None, data_prevista=None, data_completamento=None, assegnato_a=None):
    try:
        with get_session() as session:
            oa = session.get(OggettoAttivita, oa_id)
            if not oa:
                print(f"OggettoAttivita con id {oa_id} non trovato")
                return False
            if completata is not None:
                oa.completata = completata
            if data_prevista is not None:
                oa.data_prevista = data_prevista
            if data_completamento is not None:
                oa.data_completamento = data_completamento
            if assegnato_a is not None:
                oa.assegnato_a = assegnato_a
            session.commit()
            return oa_id
    except SQLAlchemyError as e:
        print(f"Errore database (update oggetto_attivita): {e}")
        return False

def delete_oggetto_attivita(oa_id):
    try:
        with get_session() as session:
            oa = session.get(OggettoAttivita, oa_id)
            if not oa:
                print(f"OggettoAttivita con id {oa_id} non trovato")
                return False
            session.delete(oa)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete oggetto_attivita): {e}")
        return False

def update_nota(nota_id, testo=None):
    try:
        with get_session() as session:
            nota = session.get(Nota, nota_id)
            if not nota:
                print(f"Nota con id {nota_id} non trovata")
                return False
            if testo is not None:
                nota.testo = testo
            session.commit()
            return nota_id
    except SQLAlchemyError as e:
        print(f"Errore database (update nota): {e}")
        return False

def delete_nota(nota_id):
    try:
        with get_session() as session:
            nota = session.get(Nota, nota_id)
            if not nota:
                print(f"Nota con id {nota_id} non trovata")
                return False
            session.delete(nota)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Errore database (delete nota): {e}")
        return False 