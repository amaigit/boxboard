import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date
import warnings
import config
warnings.filterwarnings('ignore')
from db import get_session, Utente, Location, Oggetto, Attivita, OggettoAttivita, Nota
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Configurazione della pagina
st.set_page_config(
    page_title="Sistema Svuotacantine",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
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
        return session.query(OggettoAttivita).order_by(OggettoAttivita.data_prevista).all()

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

def get_contenitori():
    """Recupera solo i contenitori"""
    return execute_query("SELECT * FROM oggetti WHERE tipo = 'contenitore' ORDER BY nome", fetch=True)

def get_oggetti_in_contenitore(contenitore_id):
    """Recupera oggetti contenuti in un contenitore specifico"""
    query = """
    SELECT o.*, l.nome as location_nome 
    FROM oggetti o
    LEFT JOIN locations l ON o.location_id = l.id
    WHERE o.contenitore_id = %s
    ORDER BY o.nome
    """
    return execute_query(query, (contenitore_id,), fetch=True)

# === INTERFACCIA UTENTE ===

def show_utenti():
    """Sezione gestione utenti"""
    st.header("👥 Gestione Utenti")
    
    # Visualizzazione utenti esistenti
    utenti = get_utenti()
    if utenti:
        df = pd.DataFrame(utenti)
        st.subheader("Utenti Registrati")
        st.dataframe(df, use_container_width=True)
    
    # Form per nuovo utente
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
                query = "INSERT INTO utenti (nome, ruolo, email) VALUES (%s, %s, %s)"
                result = execute_query(query, (nome, ruolo, email if email else None))
                if result:
                    st.success(f"Utente '{nome}' aggiunto con successo!")
                    st.rerun()
            else:
                st.error("Il nome è obbligatorio!")

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
                query = "INSERT INTO locations (nome, indirizzo, note) VALUES (%s, %s, %s)"
                result = execute_query(query, (nome, indirizzo, note))
                if result:
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
            location_options.update({loc['id']: loc['nome'] for loc in locations})
        selected_location = st.selectbox("Filtra per Location", 
                                       options=list(location_options.keys()),
                                       format_func=lambda x: location_options[x])
    
    with col2:
        stati = ["Tutti", "da_rimuovere", "smaltito", "venduto", "in_attesa", "completato"]
        selected_stato = st.selectbox("Filtra per Stato", stati)
    
    with col3:
        tipi = ["Tutti", "oggetto", "contenitore"]
        selected_tipo = st.selectbox("Filtra per Tipo", tipi)
    
    with col4:
        contenitori = get_contenitori()
        contenitore_options = {0: "Tutti i contenitori"}
        if contenitori:
            contenitore_options.update({cont['id']: cont['nome'] for cont in contenitori})
        selected_contenitore = st.selectbox("Filtra per Contenitore", 
                                          options=list(contenitore_options.keys()),
                                          format_func=lambda x: contenitore_options[x])
    
    # Applica filtri
    location_filter = selected_location if selected_location != 0 else None
    stato_filter = selected_stato if selected_stato != "Tutti" else None
    tipo_filter = selected_tipo if selected_tipo != "Tutti" else None
    
    # Visualizzazione oggetti
    oggetti = get_oggetti(location_filter, stato_filter, tipo_filter)
    
    if selected_contenitore != 0:
        # Mostra solo oggetti nel contenitore selezionato
        oggetti = [obj for obj in oggetti if obj.get('contenitore_id') == selected_contenitore]
    
    if oggetti:
        df = pd.DataFrame(oggetti)
        # Riordina colonne per visualizzazione
        cols = ['id', 'nome', 'tipo', 'stato', 'location_nome', 'contenitore_nome', 'data_rilevamento']
        df_display = df[[col for col in cols if col in df.columns]]
        st.subheader(f"Oggetti Trovati ({len(oggetti)})")
        st.dataframe(df_display, use_container_width=True)
        
        # Mostra gerarchia contenitori
        if selected_contenitore != 0:
            st.subheader("🗂️ Contenuto del Contenitore")
            contenitore_info = next((c for c in contenitori if c['id'] == selected_contenitore), None)
            if contenitore_info:
                st.info(f"Contenitore: **{contenitore_info['nome']}**")
    
    # Form per nuovo oggetto
    st.subheader("Aggiungi Nuovo Oggetto")
    with st.form("nuovo_oggetto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Oggetto*")
            tipo = st.selectbox("Tipo", ["oggetto", "contenitore"])
            stato = st.selectbox("Stato", ["da_rimuovere", "smaltito", "venduto", "in_attesa", "completato"])
        
        with col2:
            # Location
            location_id = None
            if locations:
                location_names = ["Nessuna"] + [loc['nome'] for loc in locations]
                selected_loc = st.selectbox("Location", location_names)
                if selected_loc != "Nessuna":
                    location_id = next(loc['id'] for loc in locations if loc['nome'] == selected_loc)
            
            # Contenitore (solo se tipo è 'oggetto')
            contenitore_id = None
            if tipo == "oggetto" and contenitori:
                contenitore_names = ["Nessuno"] + [cont['nome'] for cont in contenitori]
                selected_cont = st.selectbox("Contenitore", contenitore_names)
                if selected_cont != "Nessuno":
                    contenitore_id = next(cont['id'] for cont in contenitori if cont['nome'] == selected_cont)
        
        descrizione = st.text_area("Descrizione")
        
        if st.form_submit_button("Aggiungi Oggetto"):
            if nome:
                query = "INSERT INTO oggetti (nome, descrizione, stato, tipo, location_id, contenitore_id) VALUES (%s, %s, %s, %s, %s, %s)"
                result = execute_query(query, (nome, descrizione, stato, tipo, location_id, contenitore_id))
                if result:
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
                query = "INSERT INTO attivita (nome, descrizione) VALUES (%s, %s)"
                result = execute_query(query, (nome, descrizione))
                if result:
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
                selected_obj = st.selectbox("Seleziona Oggetto", range(len(oggetti)), 
                                          format_func=lambda x: oggetto_names[x])
                
                attivita_names = [att['nome'] for att in attivita]
                selected_att = st.selectbox("Seleziona Attività", range(len(attivita)), 
                                          format_func=lambda x: attivita_names[x])
            
            with col2:
                data_prevista = st.date_input("Data Prevista")
                
                utente_names = ["Nessuno"] + [utente['nome'] for utente in utenti] if utenti else ["Nessuno"]
                selected_utente = st.selectbox("Assegna a", utente_names)
            
            if st.form_submit_button("Assegna Attività"):
                oggetto_id = oggetti[selected_obj]['id']
                attivita_id = attivita[selected_att]['id']
                utente_id = None
                if selected_utente != "Nessuno" and utenti:
                    utente_id = next(u['id'] for u in utenti if u['nome'] == selected_utente)
                
                query = "INSERT INTO oggetto_attivita (oggetto_id, attivita_id, data_prevista, assegnato_a) VALUES (%s, %s, %s, %s)"
                result = execute_query(query, (oggetto_id, attivita_id, data_prevista, utente_id))
                if result:
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
        attivita_incomplete = [ass for ass in assegnazioni if not ass['completata']]
        if attivita_incomplete:
            with st.form("completa_attivita"):
                att_options = [f"{ass['oggetto_nome']} - {ass['attivita_nome']}" for ass in attivita_incomplete]
                selected_idx = st.selectbox("Seleziona Attività da Completare", range(len(attivita_incomplete)),
                                          format_func=lambda x: att_options[x])
                
                if st.form_submit_button("Completa Attività"):
                    attivita_id = attivita_incomplete[selected_idx]['id']
                    query = "UPDATE oggetto_attivita SET completata = TRUE, data_completamento = CURRENT_DATE WHERE id = %s"
                    result = execute_query(query, (attivita_id,))
                    if result:
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
            oggetto_options = ["Tutti gli oggetti"] + [f"{obj['nome']} (ID: {obj['id']})" for obj in oggetti]
            selected_obj = st.selectbox("Filtra per Oggetto", oggetto_options)
    
    with col2:
        attivita = get_attivita()
        if attivita:
            attivita_options = ["Tutte le attività"] + [att['nome'] for att in attivita]
            selected_att = st.selectbox("Filtra per Attività", attivita_options)
    
    with col3:
        locations = get_locations()
        if locations:
            location_options = ["Tutte le location"] + [loc['nome'] for loc in locations]
            selected_loc = st.selectbox("Filtra per Location", location_options)
    
    # Applica filtri
    oggetto_filter = None
    attivita_filter = None
    location_filter = None
    
    if oggetti and selected_obj != "Tutti gli oggetti":
        obj_idx = oggetto_options.index(selected_obj) - 1
        oggetto_filter = oggetti[obj_idx]['id']
    
    if attivita and selected_att != "Tutte le attività":
        att_idx = attivita_options.index(selected_att) - 1
        attivita_filter = attivita[att_idx]['id']
    
    if locations and selected_loc != "Tutte le location":
        loc_idx = location_options.index(selected_loc) - 1
        location_filter = locations[loc_idx]['id']
    
    # Visualizzazione note
    note = get_note(oggetto_filter, attivita_filter, location_filter)
    if note:
        st.subheader("Note Esistenti")
        df = pd.DataFrame(note)
        cols = ['id', 'testo', 'oggetto_nome', 'attivita_nome', 'location_nome', 'autore_nome', 'data']
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
            tipo_associazione = st.selectbox("Associa a:", ["Nessuno", "Oggetto", "Attività", "Location"])
            
            associazione_id = None
            if tipo_associazione == "Oggetto" and oggetti:
                obj_names = [f"{obj['nome']} (ID: {obj['id']})" for obj in oggetti]
                selected_obj_idx = st.selectbox("Seleziona Oggetto", range(len(oggetti)),
                                               format_func=lambda x: obj_names[x])
                associazione_id = ('oggetto', oggetti[selected_obj_idx]['id'])
            
            elif tipo_associazione == "Attività" and attivita:
                att_names = [att['nome'] for att in attivita]
                selected_att_idx = st.selectbox("Seleziona Attività", range(len(attivita)),
                                               format_func=lambda x: att_names[x])
                associazione_id = ('attivita', attivita[selected_att_idx]['id'])
            
            elif tipo_associazione == "Location" and locations:
                loc_names = [loc['nome'] for loc in locations]
                selected_loc_idx = st.selectbox("Seleziona Location", range(len(locations)),
                                               format_func=lambda x: loc_names[x])
                associazione_id = ('location', locations[selected_loc_idx]['id'])
        
        with col2:
            autore_id = None
            if utenti:
                autore_names = ["Nessuno"] + [utente['nome'] for utente in utenti]
                selected_autore = st.selectbox("Autore", autore_names)
                if selected_autore != "Nessuno":
                    autore_id = next(u['id'] for u in utenti if u['nome'] == selected_autore)
        
        if st.form_submit_button("Aggiungi Nota"):
            if testo:
                oggetto_id = associazione_id[1] if associazione_id and associazione_id[0] == 'oggetto' else None
                attivita_id = associazione_id[1] if associazione_id and associazione_id[0] == 'attivita' else None
                location_id = associazione_id[1] if associazione_id and associazione_id[0] == 'location' else None
                
                query = "INSERT INTO note (testo, oggetto_id, attivita_id, location_id, autore_id) VALUES (%s, %s, %s, %s, %s)"
                result = execute_query(query, (testo, oggetto_id, attivita_id, location_id, autore_id))
                if result:
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
        utenti_count = execute_query("SELECT COUNT(*) as count FROM utenti", fetch=True)
        count = utenti_count[0]['count'] if utenti_count else 0
        st.metric("👥 Totale Utenti", count)
    
    with col2:
        locations_count = execute_query("SELECT COUNT(*) as count FROM locations", fetch=True)
        count = locations_count[0]['count'] if locations_count else 0
        st.metric("📍 Totale Location", count)
    
    with col3:
        oggetti_count = execute_query("SELECT COUNT(*) as count FROM oggetti", fetch=True)
        count = oggetti_count[0]['count'] if oggetti_count else 0
        st.metric("📦 Totale Oggetti", count)
    
    with col4:
        attivita_count = execute_query("SELECT COUNT(*) as count FROM oggetto_attivita WHERE completata = FALSE", fetch=True)
        count = attivita_count[0]['count'] if attivita_count else 0
        st.metric("⚡ Attività Pendenti", count)
    
    st.divider()
    
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
    attivita_utenti = execute_query(query, fetch=True)
    
    if attivita_utenti:
        df = pd.DataFrame(attivita_utenti)
        st.dataframe(df, use_container_width=True)
    
    # Oggetti per stato
    st.subheader("📊 Distribuzione Oggetti per Stato")
    query = """
    SELECT stato, COUNT(*) as count
    FROM oggetti
    GROUP BY stato
    ORDER BY count DESC
    """
    stati_oggetti = execute_query(query, fetch=True)
    
    if stati_oggetti:
        col1, col2 = st.columns(2)
        with col1:
            df = pd.DataFrame(stati_oggetti)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            # Grafico a torta usando Streamlit
            st.bar_chart(df.set_index('stato'))
    
    # Attività in scadenza
    st.subheader("⏰ Attività in Scadenza")
    query = """
    SELECT o.nome as oggetto, a.nome as attivita, u.nome as assegnato_a, 
           oa.data_prevista, DATEDIFF(oa.data_prevista, CURDATE()) as giorni_rimanenti
    FROM oggetto_attivita oa
    JOIN oggetti o ON oa.oggetto_id = o.id
    JOIN attivita a ON oa.attivita_id = a.id
    LEFT JOIN utenti u ON oa.assegnato_a = u.id
    WHERE oa.completata = FALSE AND oa.data_prevista IS NOT NULL
    ORDER BY oa.data_prevista ASC
    LIMIT 10
    """
    scadenze = execute_query(query, fetch=True)
    
    if scadenze:
        df = pd.DataFrame(scadenze)
        # Colora le righe in base ai giorni rimanenti
        def color_scadenze(row):
            if row['giorni_rimanenti'] < 0:
                return ['background-color: #ffebee'] * len(row)  # Rosso chiaro per scadute
            elif row['giorni_rimanenti'] <= 3:
                return ['background-color: #fff3e0'] * len(row)  # Arancione per urgenti
            else:
                return [''] * len(row)
        
        styled_df = df.style.apply(color_scadenze, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Nessuna attività con scadenza impostata.")

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
    oggetti_location = execute_query(query, fetch=True)
    
    if oggetti_location:
        df = pd.DataFrame(oggetti_location)
        st.dataframe(df, use_container_width=True)
        
        # Grafico a barre
        st.bar_chart(df.set_index('location')['totale_oggetti'])
    
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
        rilevamenti_mese = execute_query(query, fetch=True)
        
        if rilevamenti_mese:
            df = pd.DataFrame(rilevamenti_mese)
            st.line_chart(df.set_index('mese'))
    
    with col2:
        st.write("**Attività Completate per Mese**")
        query = """
        SELECT DATE_FORMAT(data_completamento, '%Y-%m') as mese, COUNT(*) as count
        FROM oggetto_attivita
        WHERE completata = TRUE AND data_completamento >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(data_completamento, '%Y-%m')
        ORDER BY mese
        """
        completamenti_mese = execute_query(query, fetch=True)
        
        if completamenti_mese:
            df = pd.DataFrame(completamenti_mese)
            st.line_chart(df.set_index('mese'))
    
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
    performance = execute_query(query, fetch=True)
    
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
    contenitori_utilizzati = execute_query(query, fetch=True)
    
    if contenitori_utilizzati:
        df = pd.DataFrame(contenitori_utilizzati)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index('contenitore'))

# --- INSERIMENTO UTENTE ---
def add_utente(nome, ruolo, email):
    try:
        with get_session() as session:
            utente = Utente(nome=nome, ruolo=ruolo, email=email)
            session.add(utente)
            session.commit()
            return utente
    except IntegrityError as e:
        print(f"Errore di integrità (utente): {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Errore database (utente): {e}")
        return None

# --- INSERIMENTO LOCATION ---
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

# --- INSERIMENTO OGGETTO ---
def add_oggetto(nome, descrizione, stato, tipo, location_id, contenitore_id=None):
    try:
        with get_session() as session:
            oggetto = Oggetto(
                nome=nome,
                descrizione=descrizione,
                stato=stato,
                tipo=tipo,
                location_id=location_id,
                contenitore_id=contenitore_id
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

# --- INSERIMENTO ATTIVITA ---
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

# --- INSERIMENTO OGGETTO_ATTIVITA ---
def add_oggetto_attivita(oggetto_id, attivita_id, data_prevista, assegnato_a=None):
    try:
        with get_session() as session:
            oa = OggettoAttivita(
                oggetto_id=oggetto_id,
                attivita_id=attivita_id,
                data_prevista=data_prevista,
                assegnato_a=assegnato_a
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

# --- INSERIMENTO NOTA ---
def add_nota(testo, oggetto_id=None, attivita_id=None, location_id=None, autore_id=None):
    try:
        with get_session() as session:
            nota = Nota(
                testo=testo,
                oggetto_id=oggetto_id,
                attivita_id=attivita_id,
                location_id=location_id,
                autore_id=autore_id
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

# --- UPDATE UTENTE ---
def update_utente(utente_id, nome=None, ruolo=None, email=None):
    try:
        with get_session() as session:
            utente = session.get(Utente, utente_id)
            if not utente:
                return None
            if nome is not None:
                utente.nome = nome
            if ruolo is not None:
                utente.ruolo = ruolo
            if email is not None:
                utente.email = email
            session.commit()
            return utente
    except SQLAlchemyError as e:
        print(f"Errore update utente: {e}")
        return None

# --- DELETE UTENTE ---
def delete_utente(utente_id):
    try:
        with get_session() as session:
            utente = session.get(Utente, utente_id)
            if utente:
                session.delete(utente)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete utente: {e}")
        return False

# --- UPDATE LOCATION ---
def update_location(location_id, nome=None, indirizzo=None, note=None):
    try:
        with get_session() as session:
            location = session.get(Location, location_id)
            if not location:
                return None
            if nome is not None:
                location.nome = nome
            if indirizzo is not None:
                location.indirizzo = indirizzo
            if note is not None:
                location.note = note
            session.commit()
            return location
    except SQLAlchemyError as e:
        print(f"Errore update location: {e}")
        return None

# --- DELETE LOCATION ---
def delete_location(location_id):
    try:
        with get_session() as session:
            location = session.get(Location, location_id)
            if location:
                session.delete(location)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete location: {e}")
        return False

# --- UPDATE OGGETTO ---
def update_oggetto(oggetto_id, nome=None, descrizione=None, stato=None, tipo=None, location_id=None, contenitore_id=None):
    try:
        with get_session() as session:
            oggetto = session.get(Oggetto, oggetto_id)
            if not oggetto:
                return None
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
            return oggetto
    except SQLAlchemyError as e:
        print(f"Errore update oggetto: {e}")
        return None

# --- DELETE OGGETTO ---
def delete_oggetto(oggetto_id):
    try:
        with get_session() as session:
            oggetto = session.get(Oggetto, oggetto_id)
            if oggetto:
                session.delete(oggetto)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete oggetto: {e}")
        return False

# --- UPDATE ATTIVITA ---
def update_attivita(attivita_id, nome=None, descrizione=None):
    try:
        with get_session() as session:
            attivita = session.get(Attivita, attivita_id)
            if not attivita:
                return None
            if nome is not None:
                attivita.nome = nome
            if descrizione is not None:
                attivita.descrizione = descrizione
            session.commit()
            return attivita
    except SQLAlchemyError as e:
        print(f"Errore update attivita: {e}")
        return None

# --- DELETE ATTIVITA ---
def delete_attivita(attivita_id):
    try:
        with get_session() as session:
            attivita = session.get(Attivita, attivita_id)
            if attivita:
                session.delete(attivita)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete attivita: {e}")
        return False

# --- UPDATE OGGETTO_ATTIVITA ---
def update_oggetto_attivita(oa_id, completata=None, data_prevista=None, data_completamento=None, assegnato_a=None):
    try:
        with get_session() as session:
            oa = session.get(OggettoAttivita, oa_id)
            if not oa:
                return None
            if completata is not None:
                oa.completata = completata
            if data_prevista is not None:
                oa.data_prevista = data_prevista
            if data_completamento is not None:
                oa.data_completamento = data_completamento
            if assegnato_a is not None:
                oa.assegnato_a = assegnato_a
            session.commit()
            return oa
    except SQLAlchemyError as e:
        print(f"Errore update oggetto_attivita: {e}")
        return None

# --- DELETE OGGETTO_ATTIVITA ---
def delete_oggetto_attivita(oa_id):
    try:
        with get_session() as session:
            oa = session.get(OggettoAttivita, oa_id)
            if oa:
                session.delete(oa)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete oggetto_attivita: {e}")
        return False

# --- UPDATE NOTA ---
def update_nota(nota_id, testo=None, oggetto_id=None, attivita_id=None, location_id=None, autore_id=None):
    try:
        with get_session() as session:
            nota = session.get(Nota, nota_id)
            if not nota:
                return None
            if testo is not None:
                nota.testo = testo
            if oggetto_id is not None:
                nota.oggetto_id = oggetto_id
            if attivita_id is not None:
                nota.attivita_id = attivita_id
            if location_id is not None:
                nota.location_id = location_id
            if autore_id is not None:
                nota.autore_id = autore_id
            session.commit()
            return nota
    except SQLAlchemyError as e:
        print(f"Errore update nota: {e}")
        return None

# --- DELETE NOTA ---
def delete_nota(nota_id):
    try:
        with get_session() as session:
            nota = session.get(Nota, nota_id)
            if nota:
                session.delete(nota)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Errore delete nota: {e}")
        return False

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
        "📈 Statistiche": "statistiche"
    }
    
    selected = st.sidebar.selectbox(
        "🧭 Navigazione",
        options=list(menu_options.keys()),
        index=0
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

if __name__ == "__main__":
    main()
