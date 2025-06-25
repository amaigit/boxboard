import streamlit as st
import pandas as pd
from datetime import datetime, date
import warnings
import hashlib

warnings.filterwarnings("ignore")
from db import (
    get_session,
    Utente,
    Location,
    Oggetto,
    Attivita,
    OggettoAttivita,
    Nota,
    LogOperazione,
    test_db_connection,
)
from crud import add_utente, add_location, add_oggetto, add_attivita, add_oggetto_attivita, add_nota, log_operazione
# --- CONTROLLO TABELLE E POPOLAMENTO AUTOMATICO ---
try:
    with get_session() as session:
        utenti_count = session.query(Utente).count()
    if utenti_count == 0:
        test_db_connection()
        from mock_data import popola_mock
        popola_mock()
except Exception:
    # Se la tabella non esiste, crea tutto e popola
    test_db_connection()
    from mock_data import popola_mock
    popola_mock()
# --- FINE CONTROLLO ---
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_components.crud_browser import st_crud_browser
import os
from authlib.integrations.requests_client import OAuth2Session
import requests

# Configurazione della pagina
st.set_page_config(
    page_title="Sistema Svuotacantine",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === FUNZIONI CRUD ===


def get_utenti():
    """Recupera tutti gli utenti"""
    with get_session() as session:
        return session.query(Utente).order_by(Utente.nome).all()


def get_locations():
    """Recupera tutte le location"""
    with get_session() as session:
        return session.query(Location).order_by(Location.nome).all()


def get_oggetti(location_id=None, stato=None, tipo=None):
    """Recupera oggetti con filtri opzionali"""
    with get_session() as session:
        query = session.query(Oggetto)
        if location_id:
            query = query.filter(Oggetto.location_id == location_id)
        if stato:
            query = query.filter(Oggetto.stato == stato)
        if tipo:
            query = query.filter(Oggetto.tipo == tipo)
        return query.order_by(Oggetto.nome).all()


def get_attivita():
    """Recupera tutte le attività"""
    with get_session() as session:
        return session.query(Attivita).order_by(Attivita.nome).all()


def get_oggetto_attivita():
    """Recupera tutte le assegnazioni oggetto-attività"""
    with get_session() as session:
        return (
            session.query(OggettoAttivita).order_by(OggettoAttivita.data_prevista).all()
        )


def get_note(oggetto_id=None, attivita_id=None, location_id=None):
    """Recupera note con filtri opzionali"""
    with get_session() as session:
        query = session.query(Nota)
        if oggetto_id:
            query = query.filter(Nota.oggetto_id == oggetto_id)
        if attivita_id:
            query = query.filter(Nota.attivita_id == attivita_id)
        if location_id:
            query = query.filter(Nota.location_id == location_id)
        return query.order_by(Nota.data).all()


# === INTERFACCIA UTENTE ===


def show_utenti(current_user):
    """Sezione gestione utenti con controllo ruoli"""
    st.header("👥 Gestione Utenti")
    utenti = get_utenti()
    if utenti:
        df = pd.DataFrame(
            [
                {"id": u.id, "nome": u.nome, "ruolo": u.ruolo, "email": u.email}
                for u in utenti
            ]
        )
        st.subheader("Utenti Registrati")
        st.dataframe(df, use_container_width=True)

    # Solo admin (Coordinatore) può aggiungere/modificare/cancellare
    if current_user and current_user.ruolo == "Coordinatore":
        st.subheader("Aggiungi Nuovo Utente")
        with st.form("nuovo_utente"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome*")
                ruolo = st.selectbox("Ruolo", ["Operatore", "Coordinatore", "Altro"])
            with col2:
                email = st.text_input("Email")
            if st.form_submit_button("Aggiungi Utente"):
                if nome:
                    add_utente(nome, ruolo, email if email else None, current_user.id)
                    st.success(f"Utente '{nome}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.error("Il nome è obbligatorio!")
        st.subheader("Modifica/Cancella Utente")
        utente_nomi = [f"{u.nome} ({u.email})" for u in utenti]
        selected_idx = st.selectbox(
            "Seleziona utente", range(len(utenti)), format_func=lambda x: utente_nomi[x]
        )
        utente_sel = utenti[selected_idx]
        with st.form("modifica_utente"):
            col1, col2 = st.columns(2)
            with col1:
                nuovo_nome = st.text_input("Nome", value=utente_sel.nome)
                nuovo_ruolo = st.selectbox(
                    "Ruolo",
                    ["Operatore", "Coordinatore", "Altro"],
                    index=["Operatore", "Coordinatore", "Altro"].index(
                        utente_sel.ruolo
                    ),
                )
            with col2:
                nuova_email = st.text_input("Email", value=utente_sel.email)
            if st.form_submit_button("Salva Modifiche"):
                update_utente(
                    utente_sel.id,
                    nome=nuovo_nome,
                    ruolo=nuovo_ruolo,
                    email=nuova_email,
                    current_user_id=current_user.id,
                )
                st.success("Utente aggiornato!")
                st.rerun()
            if st.form_submit_button("Elimina Utente"):
                if utente_sel.id == current_user.id:
                    st.error("Non puoi eliminare te stesso!")
                else:
                    delete_utente(utente_sel.id, current_user.id)
                    st.success("Utente eliminato!")
                    st.rerun()
    else:
        st.info("Solo i Coordinatori possono modificare o cancellare utenti.")


def show_locations():
    """Sezione gestione location"""
    st.header("📍 Gestione Location")

    # Visualizzazione location esistenti
    locations = get_locations()
    if locations:
        df = pd.DataFrame(locations)
        st.subheader("Location Registrate")
        st.dataframe(df, use_container_width=True)

    # Form per nuova location
    st.subheader("Aggiungi Nuova Location")
    with st.form("nuova_location"):
        nome = st.text_input("Nome Location*")
        indirizzo = st.text_area("Indirizzo")
        note = st.text_area("Note")

        if st.form_submit_button("Aggiungi Location"):
            if nome:
                # result = execute_query(query, (nome, indirizzo, note))  # TODO: Convertire a ORM
                location = Location(nome=nome, indirizzo=indirizzo, note=note)
                with get_session() as session:
                    session.add(location)
                    session.commit()
                    st.success(f"Location '{nome}' aggiunta con successo!")
                    st.rerun()
            else:
                st.error("Il nome è obbligatorio!")


def show_oggetti():
    """Sezione gestione oggetti"""
    st.header("📦 Gestione Oggetti")

    # Filtri
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        locations = get_locations()
        location_options = {0: "Tutte le location"}
        if locations:
            location_options.update({loc["id"]: loc["nome"] for loc in locations})
        selected_location = st.selectbox(
            "Filtra per Location",
            options=list(location_options.keys()),
            format_func=lambda x: location_options[x],
        )

    with col2:
        stati = [
            "Tutti",
            "da_rimuovere",
            "smaltito",
            "venduto",
            "in_attesa",
            "completato",
        ]
        selected_stato = st.selectbox("Filtra per Stato", stati)

    with col3:
        tipi = ["Tutti", "oggetto", "contenitore"]
        selected_tipo = st.selectbox("Filtra per Tipo", tipi)

    with col4:
        contenitori = get_contenitori()
        contenitore_options = {0: "Tutti i contenitori"}
        if contenitori:
            contenitore_options.update(
                {cont["id"]: cont["nome"] for cont in contenitori}
            )
        selected_contenitore = st.selectbox(
            "Filtra per Contenitore",
            options=list(contenitore_options.keys()),
            format_func=lambda x: contenitore_options[x],
        )

    # Applica filtri
    location_filter = selected_location if selected_location != 0 else None
    stato_filter = selected_stato if selected_stato != "Tutti" else None
    tipo_filter = selected_tipo if selected_tipo != "Tutti" else None

    # Visualizzazione oggetti
    oggetti = get_oggetti(location_filter, stato_filter, tipo_filter)

    if selected_contenitore != 0:
        # Mostra solo oggetti nel contenitore selezionato
        oggetti = [
            obj for obj in oggetti if obj.get("contenitore_id") == selected_contenitore
        ]

    if oggetti:
        df = pd.DataFrame(oggetti)
        # Riordina colonne per visualizzazione
        cols = [
            "id",
            "nome",
            "tipo",
            "stato",
            "location_nome",
            "contenitore_nome",
            "data_rilevamento",
        ]
        df_display = df[[col for col in cols if col in df.columns]]
        st.subheader(f"Oggetti Trovati ({len(oggetti)})")
        st.dataframe(df_display, use_container_width=True)

        # Mostra gerarchia contenitori
        if selected_contenitore != 0:
            st.subheader("🗂️ Contenuto del Contenitore")
            contenitore_info = next(
                (c for c in contenitori if c["id"] == selected_contenitore), None
            )
            if contenitore_info:
                st.info(f"Contenitore: **{contenitore_info['nome']}**")

    # Form per nuovo oggetto
    st.subheader("Aggiungi Nuovo Oggetto")
    with st.form("nuovo_oggetto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Oggetto*")
            tipo = st.selectbox("Tipo", ["oggetto", "contenitore"])
            stato = st.selectbox(
                "Stato",
                ["da_rimuovere", "smaltito", "venduto", "in_attesa", "completato"],
            )

        with col2:
            # Location
            location_id = None
            if locations:
                location_names = ["Nessuna"] + [loc["nome"] for loc in locations]
                selected_loc = st.selectbox("Location", location_names)
                if selected_loc != "Nessuna":
                    location_id = next(
                        loc["id"] for loc in locations if loc["nome"] == selected_loc
                    )

            # Contenitore (solo se tipo è 'oggetto')
            contenitore_id = None
            if tipo == "oggetto" and contenitori:
                contenitore_names = ["Nessuno"] + [cont["nome"] for cont in contenitori]
                selected_cont = st.selectbox("Contenitore", contenitore_names)
                if selected_cont != "Nessuno":
                    contenitore_id = next(
                        cont["id"]
                        for cont in contenitori
                        if cont["nome"] == selected_cont
                    )

        descrizione = st.text_area("Descrizione")

        if st.form_submit_button("Aggiungi Oggetto"):
            if nome:
                # result = execute_query(
                #     query, (nome, descrizione, stato, tipo, location_id, contenitore_id)
                # )  # TODO: Convertire a ORM
                oggetto = Oggetto(
                    nome=nome,
                    descrizione=descrizione,
                    stato=stato,
                    tipo=tipo,
                    location_id=location_id,
                    contenitore_id=contenitore_id,
                )
                with get_session() as session:
                    session.add(oggetto)
                    session.commit()
                    st.success(f"Oggetto '{nome}' aggiunto con successo!")
                    st.rerun()
            else:
                st.error("Il nome è obbligatorio!")


def show_attivita():
    """Sezione gestione attività"""
    st.header("⚡ Gestione Attività")

    # Visualizzazione attività esistenti
    attivita = get_attivita()
    if attivita:
        df = pd.DataFrame(attivita)
        st.subheader("Attività Disponibili")
        st.dataframe(df, use_container_width=True)

    # Form per nuova attività
    st.subheader("Aggiungi Nuova Attività")
    with st.form("nuova_attivita"):
        nome = st.text_input("Nome Attività*")
        descrizione = st.text_area("Descrizione")

        if st.form_submit_button("Aggiungi Attività"):
            if nome:
                # result = execute_query(query, (nome, descrizione))  # TODO: Convertire a ORM
                attivita = Attivita(nome=nome, descrizione=descrizione)
                with get_session() as session:
                    session.add(attivita)
                    session.commit()
                    st.success(f"Attività '{nome}' aggiunta con successo!")
                    st.rerun()
            else:
                st.error("Il nome è obbligatorio!")

    # Assegnazione attività agli oggetti
    st.subheader("Assegnazione Attività")
    oggetti = get_oggetti()
    utenti = get_utenti()

    if oggetti and attivita:
        with st.form("assegna_attivita"):
            col1, col2 = st.columns(2)
            with col1:
                oggetto_names = [f"{obj['nome']} (ID: {obj['id']})" for obj in oggetti]
                selected_obj = st.selectbox(
                    "Seleziona Oggetto",
                    range(len(oggetti)),
                    format_func=lambda x: oggetto_names[x],
                )

                attivita_names = [att["nome"] for att in attivita]
                selected_att = st.selectbox(
                    "Seleziona Attività",
                    range(len(attivita)),
                    format_func=lambda x: attivita_names[x],
                )

            with col2:
                data_prevista = st.date_input("Data Prevista")

                utente_names = (
                    ["Nessuno"] + [utente["nome"] for utente in utenti]
                    if utenti
                    else ["Nessuno"]
                )
                selected_utente = st.selectbox("Assegna a", utente_names)

            if st.form_submit_button("Assegna Attività"):
                oggetto_id = oggetti[selected_obj]["id"]
                attivita_id = attivita[selected_att]["id"]
                utente_id = None
                if selected_utente != "Nessuno" and utenti:
                    utente_id = next(
                        u["id"] for u in utenti if u["nome"] == selected_utente
                    )

                # result = execute_query(
                #     query, (oggetto_id, attivita_id, data_prevista, utente_id)
                # )  # TODO: Convertire a ORM
                oa = OggettoAttivita(
                    oggetto_id=oggetto_id,
                    attivita_id=attivita_id,
                    data_prevista=data_prevista,
                    assegnato_a=utente_id,
                )
                with get_session() as session:
                    session.add(oa)
                    session.commit()
                    st.success("Attività assegnata con successo!")
                    st.rerun()

    # Visualizzazione assegnazioni esistenti
    assegnazioni = get_oggetto_attivita()
    if assegnazioni:
        st.subheader("Attività Assegnate")
        df = pd.DataFrame(assegnazioni)
        st.dataframe(df, use_container_width=True)

        # Opzione per completare attività
        st.subheader("Completa Attività")
        attivita_incomplete = [ass for ass in assegnazioni if not ass["completata"]]
        if attivita_incomplete:
            with st.form("completa_attivita"):
                att_options = [
                    f"{ass['oggetto_nome']} - {ass['attivita_nome']}"
                    for ass in attivita_incomplete
                ]
                selected_idx = st.selectbox(
                    "Seleziona Attività da Completare",
                    range(len(attivita_incomplete)),
                    format_func=lambda x: att_options[x],
                )

                if st.form_submit_button("Completa Attività"):
                    attivita_id = attivita_incomplete[selected_idx]["id"]
                    # result = execute_query(query, (attivita_id,))  # TODO: Convertire a ORM
                    query = "UPDATE oggetto_attivita SET completata = TRUE, data_completamento = CURRENT_DATE WHERE id = %s"
                    with get_session() as session:
                        session.execute(query, (attivita_id,))
                        session.commit()
                    st.success("Attività completata!")
                    st.rerun()


def show_note():
    """Sezione gestione note"""
    st.header("📝 Gestione Note")

    # Filtri per visualizzazione note
    col1, col2, col3 = st.columns(3)
    with col1:
        oggetti = get_oggetti()
        if oggetti:
            oggetto_options = ["Tutti gli oggetti"] + [
                f"{obj['nome']} (ID: {obj['id']})" for obj in oggetti
            ]
            selected_obj = st.selectbox("Filtra per Oggetto", oggetto_options)

    with col2:
        attivita = get_attivita()
        if attivita:
            attivita_options = ["Tutte le attività"] + [att["nome"] for att in attivita]
            selected_att = st.selectbox("Filtra per Attività", attivita_options)

    with col3:
        locations = get_locations()
        if locations:
            location_options = ["Tutte le location"] + [
                loc["nome"] for loc in locations
            ]
            selected_loc = st.selectbox("Filtra per Location", location_options)

    # Applica filtri
    oggetto_filter = None
    attivita_filter = None
    location_filter = None

    if oggetti and selected_obj != "Tutti gli oggetti":
        obj_idx = oggetto_options.index(selected_obj) - 1
        oggetto_filter = oggetti[obj_idx]["id"]

    if attivita and selected_att != "Tutte le attività":
        att_idx = attivita_options.index(selected_att) - 1
        attivita_filter = attivita[att_idx]["id"]

    if locations and selected_loc != "Tutte le location":
        loc_idx = location_options.index(selected_loc) - 1
        location_filter = locations[loc_idx]["id"]

    # Visualizzazione note
    note = get_note(oggetto_filter, attivita_filter, location_filter)
    if note:
        st.subheader("Note Esistenti")
        df = pd.DataFrame(note)
        cols = [
            "id",
            "testo",
            "oggetto_nome",
            "attivita_nome",
            "location_nome",
            "autore_nome",
            "data",
        ]
        df_display = df[[col for col in cols if col in df.columns]]
        st.dataframe(df_display, use_container_width=True)

    # Form per nuova nota
    st.subheader("Aggiungi Nuova Nota")
    utenti = get_utenti()

    with st.form("nuova_nota"):
        testo = st.text_area("Testo della Nota*")

        col1, col2 = st.columns(2)
        with col1:
            # Selezione tipo di associazione
            tipo_associazione = st.selectbox(
                "Associa a:", ["Nessuno", "Oggetto", "Attività", "Location"]
            )

            associazione_id = None
            if tipo_associazione == "Oggetto" and oggetti:
                obj_names = [f"{obj['nome']} (ID: {obj['id']})" for obj in oggetti]
                selected_obj_idx = st.selectbox(
                    "Seleziona Oggetto",
                    range(len(oggetti)),
                    format_func=lambda x: obj_names[x],
                )
                associazione_id = ("oggetto", oggetti[selected_obj_idx]["id"])

            elif tipo_associazione == "Attività" and attivita:
                att_names = [att["nome"] for att in attivita]
                selected_att_idx = st.selectbox(
                    "Seleziona Attività",
                    range(len(attivita)),
                    format_func=lambda x: att_names[x],
                )
                associazione_id = ("attivita", attivita[selected_att_idx]["id"])

            elif tipo_associazione == "Location" and locations:
                loc_names = [loc["nome"] for loc in locations]
                selected_loc_idx = st.selectbox(
                    "Seleziona Location",
                    range(len(locations)),
                    format_func=lambda x: loc_names[x],
                )
                associazione_id = ("location", locations[selected_loc_idx]["id"])

        with col2:
            autore_id = None
            if utenti:
                autore_names = ["Nessuno"] + [utente["nome"] for utente in utenti]
                selected_autore = st.selectbox("Autore", autore_names)
                if selected_autore != "Nessuno":
                    autore_id = next(
                        u["id"] for u in utenti if u["nome"] == selected_autore
                    )

        if st.form_submit_button("Aggiungi Nota"):
            if testo:
                # result = execute_query(
                #     query, (testo, oggetto_id, attivita_id, location_id, autore_id)
                # )  # TODO: Convertire a ORM
                oggetto_id = (
                    associazione_id[1]
                    if associazione_id and associazione_id[0] == "oggetto"
                    else None
                )
                attivita_id = (
                    associazione_id[1]
                    if associazione_id and associazione_id[0] == "attivita"
                    else None
                )
                location_id = (
                    associazione_id[1]
                    if associazione_id and associazione_id[0] == "location"
                    else None
                )

                nota = Nota(
                    testo=testo,
                    oggetto_id=oggetto_id,
                    attivita_id=attivita_id,
                    location_id=location_id,
                    autore_id=autore_id,
                )
                with get_session() as session:
                    session.add(nota)
                    session.commit()
                    st.success("Nota aggiunta con successo!")
                    st.rerun()
            else:
                st.error("Il testo della nota è obbligatorio!")


def show_dashboard():
    """Dashboard con panoramica del sistema"""
    st.header("📊 Dashboard")

    # Statistiche generali
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # utenti_count = execute_query("SELECT COUNT(*) as count FROM utenti", fetch=True)  # TODO: Convertire a ORM
        count = len(get_utenti()) if get_utenti() else 0
        st.metric("👥 Totale Utenti", count)
    with col2:
        # locations_count = execute_query("SELECT COUNT(*) as count FROM locations", fetch=True)  # TODO: Convertire a ORM
        count = len(get_locations()) if get_locations() else 0
        st.metric("📍 Totale Location", count)
    with col3:
        # oggetti_count = execute_query("SELECT COUNT(*) as count FROM oggetti", fetch=True)  # TODO: Convertire a ORM
        count = len(get_oggetti()) if get_oggetti() else 0
        st.metric("📦 Totale Oggetti", count)
    with col4:
        # attivita_count = execute_query("SELECT COUNT(*) as count FROM oggetto_attivita WHERE completata = FALSE", fetch=True)  # TODO: Convertire a ORM
        count = len([ass for ass in get_oggetto_attivita() if not ass["completata"]])
        st.metric("⚡ Attività Pendenti", count)

    st.divider()

    # --- FILTRI AVANZATI ---
    with st.expander("🔎 Filtri avanzati attività per utente", expanded=True):
        # utenti_lista = execute_query("SELECT nome FROM utenti", fetch=True)  # TODO: Convertire a ORM
        utenti_nomi = [u["nome"] for u in get_utenti()] if get_utenti() else []
        utenti_sel = st.multiselect("Filtra per utente", utenti_nomi)
        stato_sel = st.multiselect("Stato attività", ["completate", "in_corso"])
        search_txt = st.text_input("Ricerca full-text (nome utente, attività)")

    # Attività per utente
    st.subheader("📋 Attività per Utente")
    query = """
    SELECT u.nome, 
           COUNT(oa.id) as totale_attivita,
           SUM(CASE WHEN oa.completata = TRUE THEN 1 ELSE 0 END) as completate,
           SUM(CASE WHEN oa.completata = FALSE THEN 1 ELSE 0 END) as in_corso
    FROM utenti u
    LEFT JOIN oggetto_attivita oa ON u.id = oa.assegnato_a
    GROUP BY u.id, u.nome
    ORDER BY totale_attivita DESC
    """
    # attivita_utenti = execute_query(query, fetch=True)  # TODO: Convertire a ORM
    attivita_utenti = [
        {
            "nome": u["nome"],
            "totale_attivita": u["totale_attivita"],
            "completate": u["completate"],
            "in_corso": u["in_corso"],
        }
        for u in get_utenti()
    ]
    if utenti_sel:
        df = pd.DataFrame(attivita_utenti)
        df = df[df["nome"].isin(utenti_sel)]
        if stato_sel:
            if "completate" in stato_sel and "in_corso" not in stato_sel:
                df = df[df["completate"] > 0]
            elif "in_corso" in stato_sel and "completate" not in stato_sel:
                df = df[df["in_corso"] > 0]
        if search_txt:
            mask = df["nome"].str.contains(search_txt, case=False)
            df = df[mask]
        st.dataframe(df, use_container_width=True)

    # --- WIDGET AGGIUNTIVI E RESPONSIVE ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⏰ Attività Urgenti (entro 3 giorni)")
        query = """
        SELECT o.nome as oggetto, a.nome as attivita, u.nome as assegnato_a, oa.data_prevista, DATEDIFF(oa.data_prevista, CURDATE()) as giorni_rimanenti
        FROM oggetto_attivita oa
        JOIN oggetti o ON oa.oggetto_id = o.id
        JOIN attivita a ON oa.attivita_id = a.id
        LEFT JOIN utenti u ON oa.assegnato_a = u.id
        WHERE oa.completata = FALSE AND oa.data_prevista IS NOT NULL AND DATEDIFF(oa.data_prevista, CURDATE()) <= 3
        ORDER BY oa.data_prevista ASC
        LIMIT 10
        """
        # urgenti = execute_query(query, fetch=True)  # TODO: Convertire a ORM
        urgenti = [
            {
                "oggetto": u["oggetto"],
                "attivita": u["attivita"],
                "assegnato_a": u["assegnato_a"],
                "data_prevista": u["data_prevista"],
                "giorni_rimanenti": u["giorni_rimanenti"],
            }
            for u in get_oggetto_attivita()
            if not u["completata"] and u["data_prevista"] and u["data_prevista"] >= datetime.now().date()
        ]
        if urgenti:
            df = pd.DataFrame(urgenti)
            df["countdown"] = df["giorni_rimanenti"].apply(
                lambda x: f"{x} giorni" if x >= 0 else "Scaduta"
            )
            st.dataframe(
                df[
                    ["oggetto", "attivita", "assegnato_a", "data_prevista", "countdown"]
                ],
                use_container_width=True,
            )
        else:
            st.info("Nessuna attività urgente.")
    with col2:
        st.subheader("📦 Oggetti più movimentati (top 5)")
        query = """
        SELECT o.nome, COUNT(oa.id) as movimenti
        FROM oggetti o
        JOIN oggetto_attivita oa ON o.id = oa.oggetto_id
        GROUP BY o.id, o.nome
        ORDER BY movimenti DESC
        LIMIT 5
        """
        # movimentati = execute_query(query, fetch=True)  # TODO: Convertire a ORM
        movimentati = [
            {
                "nome": u["nome"],
                "movimenti": u["movimenti"],
            }
            for u in get_oggetti()
        ]
        if movimentati:
            df = pd.DataFrame(movimentati)
            st.bar_chart(df.set_index("nome")["movimenti"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessun oggetto movimentato.")

    with st.expander("📝 Storico modifiche recenti", expanded=False):
        query = """
        SELECT l.id, u.nome as utente, l.azione, l.entita, l.entita_id, l.dettagli, l.timestamp
        FROM log_operazione l
        LEFT JOIN utenti u ON l.utente_id = u.id
        ORDER BY l.timestamp DESC
        LIMIT 20
        """
        # logs = execute_query(query, fetch=True)  # TODO: Convertire a ORM
        logs = [
            {
                "id": log["id"],
                "utente": log["utente"],
                "azione": log["azione"],
                "entita": log["entita"],
                "entita_id": log["entita_id"],
                "dettagli": log["dettagli"],
                "timestamp": log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for log in get_log_operazioni()
        ]
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna modifica recente.")


def show_statistiche():
    """Sezione statistiche avanzate"""
    st.header("📈 Statistiche Avanzate")

    # Oggetti per location
    st.subheader("📍 Oggetti per Location")
    query = """
    SELECT l.nome as location, 
           COUNT(o.id) as totale_oggetti,
           SUM(CASE WHEN o.tipo = 'contenitore' THEN 1 ELSE 0 END) as contenitori,
           SUM(CASE WHEN o.tipo = 'oggetto' THEN 1 ELSE 0 END) as oggetti_semplici
    FROM locations l
    LEFT JOIN oggetti o ON l.id = o.location_id
    GROUP BY l.id, l.nome
    ORDER BY totale_oggetti DESC
    """
    # oggetti_location = execute_query(query, fetch=True)  # TODO: Convertire a ORM
    oggetti_location = [
        {
            "location": u["location"],
            "totale_oggetti": u["totale_oggetti"],
            "contenitori": u["contenitori"],
            "oggetti_semplici": u["oggetti_semplici"],
        }
        for u in get_locations()
    ]

    if oggetti_location:
        df = pd.DataFrame(oggetti_location)
        st.dataframe(df, use_container_width=True)

        # Grafico a barre
        st.bar_chart(df.set_index("location")["totale_oggetti"])

    # Statistiche temporali
    st.subheader("📅 Andamento Temporale")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Oggetti Rilevati per Mese**")
        query = """
        SELECT DATE_FORMAT(data_rilevamento, '%Y-%m') as mese, COUNT(*) as count
        FROM oggetti
        WHERE data_rilevamento >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(data_rilevamento, '%Y-%m')
        ORDER BY mese
        """
        # rilevamenti_mese = execute_query(query, fetch=True)  # TODO: Convertire a ORM
        rilevamenti_mese = [
            {
                "mese": u["mese"],
                "count": u["count"],
            }
            for u in get_oggetti()
            if u["data_rilevamento"] >= datetime.now().date() - timedelta(days=365)
        ]

        if rilevamenti_mese:
            df = pd.DataFrame(rilevamenti_mese)
            st.line_chart(df.set_index("mese"))

    with col2:
        st.write("**Attività Completate per Mese**")
        query = """
        SELECT DATE_FORMAT(data_completamento, '%Y-%m') as mese, COUNT(*) as count
        FROM oggetto_attivita
        WHERE completata = TRUE AND data_completamento >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(data_completamento, '%Y-%m')
        ORDER BY mese
        """
        # completamenti_mese = execute_query(query, fetch=True)  # TODO: Convertire a ORM
        completamenti_mese = [
            {
                "mese": u["mese"],
                "count": u["count"],
            }
            for u in get_oggetto_attivita()
            if u["completata"] and u["data_completamento"] >= datetime.now().date() - timedelta(days=365)
        ]

        if completamenti_mese:
            df = pd.DataFrame(completamenti_mese)
            st.line_chart(df.set_index("mese"))

    # Performance utenti
    st.subheader("🏆 Performance Utenti")
    query = """
    SELECT u.nome,
           COUNT(oa.id) as attivita_assegnate,
           SUM(CASE WHEN oa.completata = TRUE THEN 1 ELSE 0 END) as completate,
           ROUND(
               (SUM(CASE WHEN oa.completata = TRUE THEN 1 ELSE 0 END) * 100.0 / 
                NULLIF(COUNT(oa.id), 0)), 2
           ) as percentuale_completamento,
           AVG(DATEDIFF(oa.data_completamento, oa.data_prevista)) as ritardo_medio_giorni
    FROM utenti u
    LEFT JOIN oggetto_attivita oa ON u.id = oa.assegnato_a
    GROUP BY u.id, u.nome
    HAVING attivita_assegnate > 0
    ORDER BY percentuale_completamento DESC
    """
    # performance = execute_query(query, fetch=True)  # TODO: Convertire a ORM
    performance = [
        {
            "nome": u["nome"],
            "attivita_assegnate": u["attivita_assegnate"],
            "completate": u["completate"],
            "percentuale_completamento": u["percentuale_completamento"],
            "ritardo_medio_giorni": u["ritardo_medio_giorni"],
        }
        for u in get_utenti()
    ]

    if performance:
        df = pd.DataFrame(performance)
        st.dataframe(df, use_container_width=True)

    # Contenitori più utilizzati
    st.subheader("📦 Contenitori più Utilizzati")
    query = """
    SELECT c.nome as contenitore, COUNT(o.id) as oggetti_contenuti
    FROM oggetti c
    JOIN oggetti o ON c.id = o.contenitore_id
    WHERE c.tipo = 'contenitore'
    GROUP BY c.id, c.nome
    ORDER BY oggetti_contenuti DESC
    LIMIT 10
    """
    # contenitori_utilizzati = execute_query(query, fetch=True)  # TODO: Convertire a ORM
    contenitori_utilizzati = [
        {
            "contenitore": u["contenitore"],
            "oggetti_contenuti": u["oggetti_contenuti"],
        }
        for u in get_oggetti()
        if u["tipo"] == "contenitore"
    ]

    if contenitori_utilizzati:
        df = pd.DataFrame(contenitori_utilizzati)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("contenitore"))


def show_log_operazioni():
    st.header("📝 Log Operazioni")
    with get_session() as session:
        logs = (
            session.query(LogOperazione)
            .order_by(LogOperazione.timestamp.desc())
            .limit(100)
            .all()
        )
        if logs:
            data = [
                {
                    "id": log.id,
                    "utente": log.utente.nome if log.utente else "",
                    "azione": log.azione,
                    "entita": log.entita,
                    "entita_id": log.entita_id,
                    "dettagli": log.dettagli,
                    "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for log in logs
            ]
            st.dataframe(data, use_container_width=True)
        else:
            st.info("Nessuna operazione registrata.")


# === MAIN APP ===


def main():
    """Funzione principale dell'applicazione"""

    # Titolo principale
    st.title("🏠 Sistema Gestione Svuotacantine")
    st.markdown("---")

    # Inizializzazione database
    if st.sidebar.button("🔄 Inizializza Database"):
        with st.spinner("Creazione tabelle..."):
            if create_tables():
                st.success("✅ Database inizializzato con successo!")
            else:
                st.error("❌ Errore nell'inizializzazione del database")

    if st.sidebar.button("📋 Inserisci Dati di Esempio"):
        with st.spinner("Inserimento dati mock..."):
            if create_tables() and insert_mock_data():
                st.success("✅ Dati di esempio inseriti con successo!")
                st.rerun()
            else:
                st.error("❌ Errore nell'inserimento dei dati di esempio")

    st.sidebar.markdown("---")

    # Menu di navigazione
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "👥 Utenti": "utenti",
        "📍 Location": "locations",
        "📦 Oggetti": "oggetti",
        "⚡ Attività": "attivita",
        "📝 Note": "note",
        "📈 Statistiche": "statistiche",
    }

    selected = st.sidebar.selectbox(
        "🧭 Navigazione", options=list(menu_options.keys()), index=0
    )

    page = menu_options[selected]

    # Routing delle pagine
    if page == "dashboard":
        show_dashboard()
    elif page == "utenti":
        show_utenti()
    elif page == "locations":
        show_locations()
    elif page == "oggetti":
        show_oggetti()
    elif page == "attivita":
        show_attivita()
    elif page == "note":
        show_note()
    elif page == "statistiche":
        show_statistiche()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sistema Svuotacantine v1.0**")
    st.sidebar.markdown("Gestione completa inventario")


# --- AUTENTICAZIONE ---
def get_users_for_auth():
    """Recupera utenti dal DB e li formatta per streamlit-authenticator"""
    utenti = get_utenti()
    users = {"usernames": {}}
    for u in utenti:
        users["usernames"][u.email] = {
            "name": u.nome,
            "password": (
                u.password
                if hasattr(u, "password") and u.password
                else hashlib.sha256(u.email.encode()).hexdigest()
            ),
            "email": u.email,
            "ruolo": u.ruolo,
        }
    return users


users = get_users_for_auth()

# Configurazione autenticazione (può essere estesa per ruoli, ecc.)
authenticator = stauth.Authenticate(
    users, "boxboard_cookie", "boxboard_auth_key", cookie_expiry_days=7
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username o password errati")
if authentication_status is None:
    st.warning("Inserisci username e password")
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Autenticato come {name}")
    # Recupero utente corrente dal DB
    current_user = None
    for u in get_utenti():
        if u.email == username:
            current_user = u
            break

    # --- qui va il resto dell'app ---
    def main_router():
        menu_options = {
            "🏠 Dashboard": "dashboard",
            "👥 Utenti": "utenti",
            "📍 Location": "locations",
            "📦 Oggetti": "oggetti",
            "⚡ Attività": "attivita",
            "📝 Note": "note",
            "📈 Statistiche": "statistiche",
        }
        if current_user and current_user.ruolo == "Coordinatore":
            menu_options["📝 Log Operazioni"] = "log"
        selected = st.sidebar.selectbox(
            "🧭 Navigazione", options=list(menu_options.keys()), index=0
        )
        page = menu_options[selected]
        if page == "utenti":
            show_utenti(current_user)
        elif page == "dashboard":
            show_dashboard()
        elif page == "locations":
            show_locations()
        elif page == "oggetti":
            show_oggetti()
        elif page == "attivita":
            show_attivita()
        elif page == "note":
            show_note()
        elif page == "statistiche":
            show_statistiche()
        elif page == "log":
            show_log_operazioni()
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Sistema Svuotacantine v1.0**")
        st.sidebar.markdown("Gestione completa inventario")

    main_router()


# --- PANNELLO SCELTA MODALITÀ DB (SERVER/BROWSER) ---
def pannello_scelta_modalita():
    st.sidebar.title("Modalità database")
    scelta = st.sidebar.radio(
        "Scegli dove salvare i dati:",
        ["Server (multiutente, condiviso)", "Browser (locale, privato)"],
    )
    if scelta == "Server (multiutente, condiviso)":
        st.sidebar.info(
            "Dati salvati su database centralizzato. Ideale per collaborazione, backup, accesso remoto. Richiede configurazione DB."
        )
    else:
        st.sidebar.warning(
            "Dati salvati solo nel browser. Ideale per privacy, demo, uso offline. Rischio perdita dati se si cancella la cache/browser. Nessun invio dati al server."
        )
    st.session_state["modalita_db"] = "server" if "Server" in scelta else "browser"


# Chiamata al pannello (da inserire all'avvio app)
pannello_scelta_modalita()

# Dopo la scelta modalità, mostra il componente solo se browser
if st.session_state.get("modalita_db") == "browser":
    st.header("Gestione dati locale (modalità browser)")
    st_crud_browser()

# --- CONFIG OAUTH GOOGLE ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_SCOPE = "openid email profile"
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")


# --- FUNZIONE LOGIN GOOGLE (AUTHLIB) ---
def login_google_authlib():
    if "google_token" not in st.session_state:
        if st.button("Login con Google"):
            oauth = OAuth2Session(
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scope=GOOGLE_SCOPE,
                redirect_uri=REDIRECT_URI,
            )
            uri, state = oauth.create_authorization_url(
                GOOGLE_AUTH_URL, access_type="offline", prompt="consent"
            )
            st.session_state["oauth_state"] = state
            st.session_state["oauth_url"] = uri
            st.experimental_set_query_params()
            st.markdown(f"[Clicca qui per autenticarti con Google]({uri})")
            st.stop()
        return None
    else:
        token = st.session_state["google_token"]
        resp = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        if resp.status_code == 200:
            info = resp.json()
            email = info.get("email")
            nome = info.get("name")
            if email:
                utenti = get_utenti()
                utente = next((u for u in utenti if u.email == email), None)
                if not utente:
                    with get_session() as session:
                        nuovo = Utente(
                            nome=nome or email.split("@")[0],
                            email=email,
                            ruolo="Operatore",
                        )
                        session.add(nuovo)
                        session.commit()
                        utente = nuovo
                return utente
        return None


# --- CALLBACK OAUTH2 ---
def handle_google_callback():
    if "code" in st.experimental_get_query_params():
        code = st.experimental_get_query_params()["code"][0]
        state = st.session_state.get("oauth_state")
        oauth = OAuth2Session(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scope=GOOGLE_SCOPE,
            redirect_uri=REDIRECT_URI,
            state=state,
        )
        token = oauth.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            grant_type="authorization_code",
            client_secret=GOOGLE_CLIENT_SECRET,
        )
        st.session_state["google_token"] = token
        st.experimental_set_query_params()


# --- LOGIN UI ---
st.sidebar.header("Login")
login_method = st.sidebar.radio(
    "Metodo di accesso", ["Classico", "Google"], horizontal=True
)
current_user = None
if login_method == "Google":
    handle_google_callback()
    user_google = login_google_authlib()
    if user_google:
        st.sidebar.success(f"Autenticato come {user_google.nome} (Google)")
        current_user = user_google
        st.session_state["user_email"] = user_google.email
        st.session_state["user_nome"] = user_google.nome
        st.session_state["user_ruolo"] = user_google.ruolo
elif login_method == "Classico":
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status is False:
        st.error("Username o password errati")
    if authentication_status is None:
        st.warning("Inserisci username e password")
    if authentication_status:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Autenticato come {name}")
        utenti = get_utenti()
        for u in utenti:
            if u.email == username:
                current_user = u
                break
        st.session_state["user_email"] = current_user.email
        st.session_state["user_nome"] = current_user.nome
        st.session_state["user_ruolo"] = current_user.ruolo

# --- ROUTING SOLO SE AUTENTICATO ---
if current_user:

    def main_router():
        menu_options = {
            "🏠 Dashboard": "dashboard",
            "👥 Utenti": "utenti",
            "📍 Location": "locations",
            "📦 Oggetti": "oggetti",
            "⚡ Attività": "attivita",
            "📝 Note": "note",
            "📈 Statistiche": "statistiche",
        }
        if current_user and current_user.ruolo == "Coordinatore":
            menu_options["📝 Log Operazioni"] = "log"
        selected = st.sidebar.selectbox(
            "🧭 Navigazione", options=list(menu_options.keys()), index=0
        )
        page = menu_options[selected]
        if page == "utenti":
            show_utenti(current_user)
        elif page == "dashboard":
            show_dashboard()
        elif page == "locations":
            show_locations()
        elif page == "oggetti":
            show_oggetti()
        elif page == "attivita":
            show_attivita()
        elif page == "note":
            show_note()
        elif page == "statistiche":
            show_statistiche()
        elif page == "log":
            show_log_operazioni()
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Sistema Svuotacantine v1.0**")
        st.sidebar.markdown("Gestione completa inventario")

    main_router()

if __name__ == "__main__":
    try:
        with get_session() as session:
            utenti_count = session.query(Utente).count()
        if utenti_count == 0:
            test_db_connection()
            from mock_data import popola_mock
            popola_mock()
    except Exception:
        # Se la tabella non esiste, crea tutto e popola
        test_db_connection()
        from mock_data import popola_mock
        popola_mock()
    main()
