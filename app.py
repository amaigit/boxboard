import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date
import warnings
import config
warnings.filterwarnings('ignore')
from db import get_session, Utente, Location, Oggetto, Attivita, OggettoAttivita, Nota

# Configurazione della pagina
st.set_page_config(
    page_title="Sistema Svuotacantine",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurazione database
DB_CONFIG = {
    'host': config.DB_HOST,
    'database': config.DB_NAME,
    'user': config.DB_USER,
    'password': config.DB_PASSWORD,
    'port': config.DB_PORT
}

@st.cache_resource
def init_connection():
    """Inizializza la connessione al database MariaDB"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Errore connessione database: {e}")
        return None

def get_db_connection():
    """Ottiene una nuova connessione al database"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        st.error(f"Errore connessione database: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Esegue una query sul database"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Error as e:
        st.error(f"Errore query: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_tables():
    """Crea le tabelle nel database se non esistono"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Abilita chiavi esterne
        cursor.execute("SET foreign_key_checks = 1;")
        
        # Tabella utenti
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            ruolo ENUM('Operatore', 'Coordinatore', 'Altro') DEFAULT 'Operatore',
            email VARCHAR(255) UNIQUE,
            INDEX idx_email (email)
        ) ENGINE=InnoDB;
        """)
        
        # Tabella locations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            indirizzo TEXT,
            note TEXT,
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_nome (nome)
        ) ENGINE=InnoDB;
        """)
        
        # Tabella oggetti
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS oggetti (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descrizione TEXT,
            stato ENUM('da_rimuovere', 'smaltito', 'venduto', 'in_attesa', 'completato') DEFAULT 'da_rimuovere',
            tipo ENUM('oggetto', 'contenitore') DEFAULT 'oggetto',
            location_id INT,
            contenitore_id INT,
            data_rilevamento DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
            FOREIGN KEY (contenitore_id) REFERENCES oggetti(id) ON DELETE SET NULL,
            INDEX idx_location (location_id),
            INDEX idx_contenitore (contenitore_id),
            INDEX idx_stato (stato),
            INDEX idx_tipo (tipo)
        ) ENGINE=InnoDB;
        """)
        
        # Tabella attivita
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attivita (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descrizione TEXT
        ) ENGINE=InnoDB;
        """)
        
        # Tabella oggetto_attivita
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS oggetto_attivita (
            id INT AUTO_INCREMENT PRIMARY KEY,
            oggetto_id INT NOT NULL,
            attivita_id INT NOT NULL,
            completata BOOLEAN DEFAULT FALSE,
            data_prevista DATE,
            data_completamento DATE,
            assegnato_a INT,
            FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
            FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
            FOREIGN KEY (assegnato_a) REFERENCES utenti(id) ON DELETE SET NULL,
            INDEX idx_oggetto (oggetto_id),
            INDEX idx_attivita (attivita_id),
            INDEX idx_assegnato (assegnato_a),
            INDEX idx_completata (completata)
        ) ENGINE=InnoDB;
        """)
        
        # Tabella note
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS note (
            id INT AUTO_INCREMENT PRIMARY KEY,
            testo TEXT NOT NULL,
            oggetto_id INT NULL,
            attivita_id INT NULL,
            location_id INT NULL,
            autore_id INT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
            FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
            FOREIGN KEY (autore_id) REFERENCES utenti(id) ON DELETE SET NULL,
            INDEX idx_oggetto (oggetto_id),
            INDEX idx_attivita (attivita_id),
            INDEX idx_location (location_id),
            INDEX idx_autore (autore_id)
        ) ENGINE=InnoDB;
        """)
        
        conn.commit()
        return True
        
    except Error as e:
        st.error(f"Errore creazione tabelle: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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

def insert_mock_data():
    """Inserisce dati di esempio nel database"""
    try:
        # Utenti
        utenti_mock = [
            ("Mario Rossi", "Coordinatore", "mario.rossi@email.com"),
            ("Luigi Verdi", "Operatore", "luigi.verdi@email.com"),
            ("Anna Bianchi", "Operatore", "anna.bianchi@email.com"),
            ("Giulia Neri", "Altro", "giulia.neri@email.com")
        ]
        
        for nome, ruolo, email in utenti_mock:
            query = "INSERT IGNORE INTO utenti (nome, ruolo, email) VALUES (%s, %s, %s)"
            execute_query(query, (nome, ruolo, email))
        
        # Locations
        locations_mock = [
            ("Magazzino Centrale", "Via Roma 123, Milano", "Magazzino principale"),
            ("Deposito Nord", "Via Garibaldi 45, Brescia", "Deposito secondario"),
            ("Cantina Palazzo", "Piazza Duomo 12, Milano", "Cantina storica"),
            ("Garage Privato", "Via Manzoni 78, Bergamo", "Garage residenziale")
        ]
        
        for nome, indirizzo, note in locations_mock:
            query = "INSERT IGNORE INTO locations (nome, indirizzo, note) VALUES (%s, %s, %s)"
            execute_query(query, (nome, indirizzo, note))
        
        # Attività
        attivita_mock = [
            ("Valutazione", "Valutare il valore dell'oggetto"),
            ("Trasporto", "Trasportare l'oggetto al deposito"),
            ("Pulizia", "Pulire e igienizzare l'oggetto"),
            ("Catalogazione", "Catalogare e fotografare l'oggetto"),
            ("Vendita", "Mettere in vendita l'oggetto"),
            ("Smaltimento", "Smaltire l'oggetto secondo normative")
        ]
        
        for nome, descrizione in attivita_mock:
            query = "INSERT IGNORE INTO attivita (nome, descrizione) VALUES (%s, %s)"
            execute_query(query, (nome, descrizione))
        
        # Oggetti (prima i contenitori, poi gli oggetti)
        contenitori_mock = [
            ("Scatola Grande Cartone", "Scatola di cartone 60x40x40cm", "da_rimuovere", "contenitore", 1),
            ("Baule Antico", "Baule in legno d'epoca", "in_attesa", "contenitore", 2),
            ("Cassetta Plastica", "Cassetta in plastica trasparente", "da_rimuovere", "contenitore", 1),
            ("Valigia Vintage", "Valigia anni '70 in pelle", "venduto", "contenitore", 3)
        ]
        
        for nome, descrizione, stato, tipo, location_id in contenitori_mock:
            query = "INSERT INTO oggetti (nome, descrizione, stato, tipo, location_id) VALUES (%s, %s, %s, %s, %s)"
            execute_query(query, (nome, descrizione, stato, tipo, location_id))
        
        # Oggetti semplici
        oggetti_mock = [
            ("Lampada da Tavolo", "Lampada vintage in ottone", "da_rimuovere", "oggetto", 1, 1),
            ("Libro di Cucina", "Ricettario della nonna", "completato", "oggetto", 1, 1),
            ("Orologio da Parete", "Orologio a pendolo", "in_attesa", "oggetto", 2, 2),
            ("Servizio Piatti", "Set di piatti per 6 persone", "venduto", "oggetto", 3, 4),
            ("Macchina da Scrivere", "Olivetti anni '60", "smaltito", "oggetto", 2, None),
            ("Poltrona", "Poltrona in pelle marrone", "da_rimuovere", "oggetto", 4, None),
            ("Quadro", "Dipinto paesaggio montano", "venduto", "oggetto", 3, None),
            ("Specchio", "Specchio con cornice dorata", "in_attesa", "oggetto", 1, 3)
        ]
        
        for nome, descrizione, stato, tipo, location_id, contenitore_id in oggetti_mock:
            query = "INSERT INTO oggetti (nome, descrizione, stato, tipo, location_id, contenitore_id) VALUES (%s, %s, %s, %s, %s, %s)"
            execute_query(query, (nome, descrizione, stato, tipo, location_id, contenitore_id))
        
        # Assegnazioni attività (assumendo che gli ID siano sequenziali)
        assegnazioni_mock = [
            (1, 1, False, "2024-07-01", None, 1),  # Lampada - Valutazione - Mario
            (1, 3, True, "2024-06-15", "2024-06-14", 2),   # Lampada - Pulizia - Luigi (completata)
            (3, 2, False, "2024-07-10", None, 1),  # Orologio - Trasporto - Mario
            (6, 1, False, "2024-07-05", None, 3),  # Poltrona - Valutazione - Anna
            (8, 4, True, "2024-06-20", "2024-06-18", 2),   # Specchio - Catalogazione - Luigi (completata)
        ]
        
        for oggetto_id, attivita_id, completata, data_prevista, data_completamento, assegnato_a in assegnazioni_mock:
            query = """INSERT INTO oggetto_attivita 
                      (oggetto_id, attivita_id, completata, data_prevista, data_completamento, assegnato_a) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            execute_query(query, (oggetto_id, attivita_id, completata, data_prevista, data_completamento, assegnato_a))
        
        # Note
        note_mock = [
            ("Oggetto in buone condizioni, da valutare per vendita", 1, None, None, 1),
            ("Trasporto programmato per venerdì mattina", None, 2, None, 2),
            ("Location molto umida, attenzione alla muffa", None, None, 3, 1),
            ("Attività completata in anticipo rispetto alla scadenza", None, 1, None, 3)
        ]
        
        for testo, oggetto_id, attivita_id, location_id, autore_id in note_mock:
            query = "INSERT INTO note (testo, oggetto_id, attivita_id, location_id, autore_id) VALUES (%s, %s, %s, %s, %s)"
            execute_query(query, (testo, oggetto_id, attivita_id, location_id, autore_id))
        
        return True
        
    except Exception as e:
        st.error(f"Errore inserimento dati mock: {e}")
        return False

# --- INSERIMENTO UTENTE ---
def add_utente(nome, ruolo, email):
    with get_session() as session:
        utente = Utente(nome=nome, ruolo=ruolo, email=email)
        session.add(utente)
        session.commit()
        return utente

# --- INSERIMENTO LOCATION ---
def add_location(nome, indirizzo, note):
    with get_session() as session:
        location = Location(nome=nome, indirizzo=indirizzo, note=note)
        session.add(location)
        session.commit()
        return location

# --- INSERIMENTO OGGETTO ---
def add_oggetto(nome, descrizione, stato, tipo, location_id, contenitore_id=None):
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

# --- INSERIMENTO ATTIVITA ---
def add_attivita(nome, descrizione):
    with get_session() as session:
        attivita = Attivita(nome=nome, descrizione=descrizione)
        session.add(attivita)
        session.commit()
        return attivita

# --- INSERIMENTO OGGETTO_ATTIVITA ---
def add_oggetto_attivita(oggetto_id, attivita_id, data_prevista, assegnato_a=None):
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

# --- INSERIMENTO NOTA ---
def add_nota(testo, oggetto_id=None, attivita_id=None, location_id=None, autore_id=None):
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
