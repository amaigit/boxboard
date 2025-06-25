# Piano di Lavoro per il Recupero e Completamento di BoxBoard

Questo documento elenca i passi da seguire per rendere il progetto coerente, manutenibile e realmente multi-database. Ogni punto verrà spuntato al completamento.

---

## Fase 1: Fondamenta e coerenza
- [x] **Separazione della configurazione**
  - Creato file `.env.example` con i parametri di esempio per la connessione al database (il file `.env` reale va creato localmente e non va committato).
  - Creato modulo `config.py` che carica le variabili dal file `.env` tramite python-dotenv.
  - Aggiornato `requirements.txt` aggiungendo la dipendenza python-dotenv.
  - Modificato `app.py` per usare la configurazione esterna invece dei parametri hardcoded.

- [ ] **Astrazione del database**
  - [x] Aggiunte dipendenze SQLAlchemy e driver per MariaDB/MySQL, PostgreSQL, SQLite in `requirements.txt`.
  - [x] Creato modulo `db.py` che gestisce la connessione e la sessione SQLAlchemy in base al tipo di database scelto in configurazione.
  - [x] Definiti i modelli ORM SQLAlchemy per tutte le tabelle (utenti, locations, oggetti, attivita, oggetto_attivita, note).
  - [x] Test di connessione e creazione tabelle su tutti i DB supportati tramite funzione dedicata in `db.py`.
  - [x] Compatibilità cross-DB dei modelli ORM (Enum e relazioni) garantita.
  - [x] Script di test CRUD automatico integrato nel progetto (`test_crud.py`).
  - [x] Verifica e validazione degli script SQL di creazione per MariaDB, PostgreSQL e SQLite.

- [ ] **Refactoring del codice**
  - [x] Iniziato il refactoring delle funzioni CRUD in `app.py` per usare SQLAlchemy ORM (lettura dati: utenti, locations, oggetti, attività, assegnazioni, note).
  - [x] Completato il refactoring delle funzioni di inserimento (add) per tutte le entità principali con SQLAlchemy ORM.
  - [x] Completato il refactoring CRUD (modifica, cancellazione) per tutte le entità principali con SQLAlchemy ORM.
  - [x] Garantita la compatibilità delle query CRUD con tutti i DB supportati.

---

## Fase 2: Robustezza e usabilità
- [x] **Gestione degli errori e messaggi chiari**
  - Aggiunta gestione try/except e messaggi d'errore chiari nelle funzioni CRUD.

- [x] **Aggiornamento della documentazione**
  - Aggiornato il `README.md` con istruzioni multi-database, test CRUD e aggiunta nuovi DBMS.

- [x] **Aggiunta di dati di esempio e test**
  - Funzione/script per popolare il database con dati di esempio (`mock_data.py`).
  - (Opzionale) Aggiungere test automatici per le funzioni principali.

---

## Fase 3: Migliorie e manutenzione
- [x] **Pulizia e ottimizzazione del codice**
  - Rimosso tutto il codice legacy, commenti inutili, variabili hardcoded e adattato tutto all'uso degli oggetti ORM.

- [ ] **Estensione delle funzionalità**
  - Solo dopo aver sistemato la base, valutare nuove feature o miglioramenti (es. autenticazione, esportazione dati, API REST, ecc.).

---

## Sequenza operativa consigliata
1. Configurazione esterna (`.env`/`config.py`)
2. Modulo di astrazione DB
3. Refactoring funzioni CRUD
4. Test su tutti i DB supportati
5. Documentazione aggiornata
6. Dati di esempio e test
7. Pulizia e ottimizzazione 

---

## Prossime feature pianificate

### 1. Autenticazione e gestione utenti
- [x] Iniziata integrazione di streamlit-authenticator per login/logout e sessione utente
- [x] Gestione ruoli (admin, operatore, solo lettura, ecc.)
- [x] Interfaccia per creazione/modifica/cancellazione utenti (solo admin)
- [x] Possibilità di tracciare chi esegue le operazioni
- [ ] (Opzionale) Integrazione con provider esterni (Google, LDAP, OAuth2)
- Possibili strumenti: [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator), custom component

### 2. API REST
- Esporre le funzionalità CRUD tramite API RESTful (ad esempio con FastAPI o Flask)
- Documentazione API (OpenAPI/Swagger)
- Gestione autenticazione/permessi anche sulle API
- Possibilità di filtrare, esportare, importare dati tramite API
- Integrazione con altre app, automazioni, mobile, ecc.
- Possibili strumenti: FastAPI, Flask, JWT per autenticazione

### 3. Dashboard avanzata
- [x] Filtri e ricerca avanzata (sidebar/barra filtri, st.text_input, st.selectbox, st.multiselect, ricerca full-text)
- [ ] Widget aggiuntivi e layout responsive (st.columns, st.expander, nuovi widget)
- [ ] Commit e push su GitHub ad ogni step

---

## Piano dettagliato sviluppo API REST

### Obiettivo generale
Esporre tutte le funzionalità del sistema tramite API RESTful, in modo che ogni operazione sia eseguibile sia dal frontend Streamlit che da client alternativi (web, mobile, automazioni, ecc.).

### Stack scelto
- **FastAPI** per API REST (veloce, moderna, OpenAPI integrato)
- **Autenticazione JWT** (login, permessi, ruoli)
- **Compatibilità con ORM SQLAlchemy già esistente**

### Fasi di sviluppo

#### Fase 1: Setup e autenticazione
- [x] Creazione file `api.py` e struttura base FastAPI
- [x] Endpoint di healthcheck (`/health`)
- [x] Endpoint di autenticazione (login, refresh token)
- [x] Gestione JWT e permessi per ruoli (Operatore, Coordinatore, Altro)
- [x] Documentazione OpenAPI automatica

#### Fase 2: Utenti
- [x] Endpoint CRUD utenti (solo admin può creare/modificare/cancellare)
- [x] Endpoint per cambiare la propria password
- [x] Endpoint per ottenere il proprio profilo
- [x] Protezione permessi su ogni endpoint

#### Fase 3: Location
- [x] Endpoint CRUD location
- [x] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 4: Oggetti
- [x] Endpoint CRUD oggetti
- [x] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 5: Attività
- [x] Endpoint CRUD attività
- [x] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 6: Note
- [x] Endpoint CRUD note
- [x] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 7: Log operazioni
- [x] Endpoint per consultare il log delle operazioni (solo admin)

#### Fase 8: Extra e ottimizzazioni
- [x] Endpoint per esportazione/importazione dati (CSV/JSON)
- [x] Rate limiting, CORS, sicurezza
- [x] Test automatici delle API
- [x] Aggiornamento documentazione

### Modalità di lavoro
- Ogni fase/milestone sarà committata separatamente
- La documentazione sarà aggiornata progressivamente
- Possibilità di modificare/estendere il piano in base a nuove esigenze 

---

## Modalità database: server e browser

Per la pianificazione dettagliata vedi anche [PIANIFICAZIONE_MODALITA_DB.md](./PIANIFICAZIONE_MODALITA_DB.md)

### Obiettivo
Consentire all'utente di scegliere, tramite interfaccia Streamlit, se:
- Collegarsi a un database server-side (MariaDB, PostgreSQL, SQLite, anche remoto)
- Gestire tutti i dati solo nel browser (modalità locale/privata, senza invio dati al server)

### User Story principali
- Come utente voglio scegliere la modalità di gestione dati (server o browser) dal pannello impostazioni.
- Come utente voglio essere informato sui vantaggi/limiti di ciascuna modalità.
- Come utente voglio poter esportare/importare i miei dati tra le due modalità.

### Analisi tecnica
- Modalità server: già implementata (SQLAlchemy, DB configurabile via .env o pannello).
- Modalità browser: da implementare, richiede componente Streamlit custom (JS/IndexedDB o sql.js).
- Sincronizzazione: solo tramite esportazione/importazione manuale.
- Sicurezza: dati browser solo locali, nessun invio al server.

### Scelta tecnica
- Per la modalità browser verrà utilizzato **IndexedDB** tramite la libreria [Dexie.js](https://dexie.org/), che offre API moderne e semplici per CRUD locale, storage ampio e buona compatibilità cross-browser.
- Dexie.js semplifica la gestione delle tabelle e delle query rispetto all'API IndexedDB nativa.
- In futuro si potrà valutare l'uso di sql.js o wa-sqlite se servirà compatibilità SQL o esportazione in formato SQLite.

### Roadmap di sviluppo (modalità browser)
1. Progettazione UX pannello di scelta modalità (Streamlit)
2. Implementazione Streamlit Component custom per CRUD locale con Dexie.js
3. Integrazione logica di scelta e fallback tra modalità server/browser
4. Esportazione/importazione dati tra modalità (JSON)
5. Test cross-browser e documentazione

### Rischi e note
- La modalità browser è ideale per privacy, demo, uso offline, ma non per collaborazione.
- La scelta della modalità deve essere chiara e reversibile per l'utente.
- L'implementazione richiede competenze sia Python/Streamlit che JavaScript/WebAssembly.

- [x] Progettazione UX pannello di scelta modalità (Streamlit)
- [x] Struttura base componente custom (frontend JS + backend Python)
- [x] Integrazione condizionale in Streamlit (solo modalità browser)
- [x] CRUD locale per tutte le entità principali
- [x] Esportazione/importazione dati (JSON)
- [x] Test cross-browser e documentazione
- [x] Logica JS Dexie.js per CRUD locale, esportazione/importazione e sync manuale pronta all'integrazione

---

## Sincronizzazione dati browser/server

### Obiettivo
Permettere all'utente di sincronizzare i dati tra modalità browser (IndexedDB/Dexie.js) e backend server (API REST).

### Roadmap
- [x] Progettazione UX per sincronizzazione manuale (pulsanti "Sincronizza con server")
- [x] Endpoint API per import/export bulk (JSON)
- [ ] Integrazione pulsanti di sync nel componente browser
- [x] Documentazione e warning su conflitti/merge
- [x] Sincronizzazione automatica dati locali/server (Dexie.js + API REST)

---

## Roadmap avanzata e ottimizzazione (2024)

### 1. Sicurezza e best practice
- [x] Restringere CORS in produzione (solo domini autorizzati)
- [x] Migliorare gestione variabili di ambiente e segreti
- [x] Documentare best practice di sicurezza (README)
- [ ] (Opzionale) Rate limiting reale sulle API

### 2. Automazione e qualità
- [x] Aggiungere workflow CI/CD (GitHub Actions) per test automatici su push/pull request
- [x] Badge di stato build/test nel README
- [ ] (Opzionale) Linting e formattazione automatica

### 3. Feature avanzate (opzionali)
- [ ] Sincronizzazione dati browser/server (manuale o automatica)
- [ ] Provider di autenticazione esterni (Google, LDAP, ecc.)
- [ ] Dashboard avanzata, filtri, ricerca full-text
- [ ] Notifiche, log avanzato, audit trail

### 4. Funzionalità avanzate browser
- [x] Sincronizzazione automatica dati locali/server (Dexie.js + API REST)
- [x] UI CRUD interattiva (tabella dinamica, modali, filtri, ricerca)
- [x] Notifiche avanzate (successo, errore, stato online/offline, storico operazioni)
- [x] Commit e push su GitHub ad ogni step

### 5. Dashboard avanzata
- [x] Filtri e ricerca avanzata (sidebar/barra filtri, st.text_input, st.selectbox, st.multiselect, ricerca full-text)
- [ ] Widget aggiuntivi e layout responsive (st.columns, st.expander, nuovi widget)
- [ ] Commit e push su GitHub ad ogni step

--- 