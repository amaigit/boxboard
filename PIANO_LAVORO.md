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
- [ ] Documentazione OpenAPI automatica

#### Fase 2: Utenti
- [x] Endpoint CRUD utenti (solo admin può creare/modificare/cancellare)
- [x] Endpoint per cambiare la propria password
- [x] Endpoint per ottenere il proprio profilo
- [x] Protezione permessi su ogni endpoint

#### Fase 3: Location
- [x] Endpoint CRUD location
- [ ] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 4: Oggetti
- [x] Endpoint CRUD oggetti
- [ ] Endpoint per ricerca/filtri avanzati
- [ ] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 5: Attività
- [x] Endpoint CRUD attività
- [ ] Endpoint per assegnazione attività a oggetti/utenti
- [ ] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 6: Note
- [ ] Endpoint CRUD note
- [ ] Permessi: tutti possono leggere, solo admin può modificare/cancellare

#### Fase 7: Log operazioni
- [ ] Endpoint per consultare il log delle operazioni (solo admin)

#### Fase 8: Extra e ottimizzazioni
- [ ] Endpoint per esportazione/importazione dati (CSV/JSON)
- [ ] Rate limiting, CORS, sicurezza
- [ ] Test automatici delle API
- [ ] Aggiornamento documentazione

### Modalità di lavoro
- Ogni fase/milestone sarà committata separatamente
- La documentazione sarà aggiornata progressivamente
- Possibilità di modificare/estendere il piano in base a nuove esigenze 