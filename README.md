# BoxBoard

![Boxboard Logo](https://github.com/amaigit/boxboard/raw/main/assets/logo.png)

[![Build Status](https://github.com/amaigit/boxboard/actions/workflows/ci.yml/badge.svg)](https://github.com/amaigit/boxboard/actions)

**Boxboard** è un'applicazione web sviluppata con [Streamlit](https://streamlit.io/) per la gestione di oggetti e contenitori in scenari di svuotamento cantine, magazzini o archiviazione. Consente di tracciare oggetti, assegnare attività, gestire contenitori e visualizzare statistiche in tempo reale.

🔗 **Demo online**: [boxboard.streamlit.app](https://boxboard.streamlit.app)

---

## 🚀 Funzionalità principali

* **Gestione oggetti e contenitori**: aggiungi, modifica e visualizza oggetti e contenitori associati.
* **Assegnazione attività**: crea attività, assegnale a utenti e monitora lo stato di completamento.
* **Dashboard interattiva**: visualizza statistiche e attività in tempo reale.
* **Supporto per più database**: compatibile con MariaDB, PostgreSQL e SQLite.

---

## 🛠️ Requisiti

* Python 3.10+
* Streamlit
* mysql-connector-python
* pandas
* warnings (incluso in Python)

---

## 📦 Installazione

1. Clona il repository:

   ```bash
   git clone https://github.com/amaigit/boxboard.git
   cd boxboard
   ```

2. Crea un ambiente virtuale e attivalo:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. Installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura il database:

   - Modifica il file `.env` secondo le tue esigenze (vedi sezione sopra).
   - Inizializza il database con lo script SQL appropriato **solo se vuoi popolare manualmente** (opzionale, normalmente SQLAlchemy crea le tabelle automaticamente).

5. Avvia l'app:

   ```bash
   streamlit run app.py
   ```

---

## 📄 Struttura del progetto

```
boxboard/
├── app.py                  # Codice principale dell'app Streamlit
├── db.py                   # Modulo di astrazione e modelli ORM SQLAlchemy
├── config.py               # Configurazione centralizzata (carica variabili da .env)
├── test_crud.py            # Script di test CRUD automatico multi-database
├── createdb-mariadb.sql    # Script di creazione del database per MariaDB
├── createdb-pg.sql         # Script di creazione del database per PostgreSQL
├── createdb-sqlite.sql     # Script di creazione del database per SQLite
├── requirements.txt        # Dipendenze del progetto
├── .env.example            # Esempio di configurazione ambiente
├── .gitignore              # File per ignorare file non necessari nel controllo versione
└── README.md               # Documentazione del progetto
```

---

## 🤝 Contribuire

Contribuire a Boxboard è semplice:

1. Fork del repository
2. Crea un nuovo branch (`git checkout -b feature-nome`)
3. Apporta le modifiche desiderate
4. Commit delle modifiche (`git commit -am 'Aggiungi nuova funzionalità'`)
5. Push del branch (`git push origin feature-nome`)
6. Crea una pull request

---

## 📄 Licenza

Distribuito sotto la licenza MIT. Vedi il file [LICENSE](LICENSE) per ulteriori dettagli.

---

Se desideri aggiungere ulteriori sezioni o dettagli specifici, fammi sapere!

## ⚙️ Configurazione multi-database

La configurazione del database avviene tramite il file `.env` (vedi `.env.example`).
Esempio:

```
DB_TYPE=mariadb        # oppure postgresql oppure sqlite
DB_HOST=localhost      # non necessario per sqlite
DB_PORT=3306           # 5432 per PostgreSQL, non necessario per sqlite
DB_NAME=svuotacantine  # per sqlite sarà il nome del file .db
DB_USER=root           # non necessario per sqlite
DB_PASSWORD=password   # non necessario per sqlite
```

- Per **SQLite** basta impostare `DB_TYPE=sqlite` e `DB_NAME=boxboard` (verrà creato `boxboard.db`).
- Per **PostgreSQL** e **MariaDB/MySQL** assicurati che il database esista e che i parametri siano corretti.

---

## 🧪 Test CRUD automatici

Per verificare che tutte le operazioni CRUD funzionino su qualsiasi database, esegui:

```bash
python test_crud.py
```

Se tutti i test sono superati, la configurazione è corretta!

---

## ➕ Aggiungere un nuovo DBMS

1. Aggiungi il driver SQLAlchemy appropriato a `requirements.txt`.
2. Modifica `db.py` aggiungendo la stringa di connessione per il nuovo DBMS.
3. Aggiorna `.env.example` e la documentazione.
4. (Opzionale) Adatta gli script SQL di creazione se vuoi supportare anche l'inizializzazione manuale.

## 🌐 Connessione a database remoto

L'applicazione può collegarsi a un database remoto (MariaDB/MySQL, PostgreSQL) semplicemente configurando il file `.env` con i parametri del server remoto.

### Esempio MariaDB/MySQL remoto
```
DB_TYPE=mariadb
DB_HOST=123.123.123.123      # IP o hostname del server remoto
DB_PORT=3306
DB_NAME=svuotacantine
DB_USER=nomeutente
DB_PASSWORD=supersegreta
```

### Esempio PostgreSQL remoto
```
DB_TYPE=postgresql
DB_HOST=db.miosito.com
DB_PORT=5432
DB_NAME=svuotacantine
DB_USER=nomeutente
DB_PASSWORD=supersegreta
```

#### Requisiti per la connessione remota
- Il database deve essere accessibile dalla macchina/server dove gira Streamlit (deve poter raggiungere l'IP/hostname e la porta del DB).
- Il database remoto deve accettare connessioni esterne (non solo da localhost).
- Le credenziali devono essere corrette e l'utente deve avere i permessi necessari.
- Il firewall del server DB deve permettere le connessioni in ingresso sulla porta del database.

#### Consigli di sicurezza
- Usa password robuste e, se possibile, connessioni cifrate (SSL/TLS).
- Non esporre il database direttamente su Internet senza protezioni (VPN, firewall, whitelist IP).

#### Troubleshooting
- Se la connessione fallisce, verifica:
  - Che il server DB sia in ascolto sull'IP/porta giusti
  - Che il firewall non blocchi la porta
  - Che l'utente abbia i permessi di accesso da remoto
  - Che i parametri in `.env` siano corretti

## Autenticazione e gestione utenti

L'app ora richiede autenticazione tramite [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator):
- All'avvio viene richiesto login (username = email, password = hash/email se non presente)
- Logout disponibile nella sidebar
- Solo utenti autenticati possono accedere alle funzionalità
- Gli utenti sono letti dalla tabella `utenti` del database
- Per ora la gestione utenti (creazione/modifica/cancellazione) va fatta direttamente sul database

Prossimi sviluppi:
- Gestione ruoli (admin, operatore, solo lettura)
- Interfaccia per gestione utenti
- Integrazione provider esterni (Google, LDAP, ecc.)

## Gestione ruoli

- Ogni utente ha un ruolo: **Operatore**, **Coordinatore** (admin), **Altro**
- Solo i Coordinatori possono aggiungere, modificare o cancellare utenti
- Gli altri ruoli possono solo visualizzare la lista utenti

## Interfaccia gestione utenti

- Sezione dedicata nella sidebar
- Visualizzazione tabellare di tutti gli utenti
- Form per aggiungere nuovo utente (solo Coordinatore)
- Modifica/cancellazione utenti esistenti (solo Coordinatore)
- Un Coordinatore non può eliminare se stesso

## Tracciamento delle operazioni

- Tutte le operazioni di creazione, modifica e cancellazione utenti vengono registrate in una tabella di log
- I Coordinatori possono visualizzare il log delle ultime 100 operazioni dalla sidebar (voce "Log Operazioni")
- Il log mostra: chi ha eseguito l'azione, tipo di operazione, entità coinvolta, dettagli e data/ora

## API REST

Le principali funzionalità CRUD sono esposte tramite FastAPI:
- Autenticazione JWT (login)
- CRUD utenti (solo admin)
- CRUD location, oggetti, attività, note (lettura per tutti, modifica/cancellazione solo admin)
- Log operazioni (solo admin)
- Esportazione dati (CSV/JSON) per tutte le entità principali (solo admin)

### Documentazione interattiva

- OpenAPI/Swagger: `/docs`
- Redoc: `/redoc`

### Esempio di login e uso token

1. POST `/login` con form-data `username` e `password` per ottenere il token JWT
2. Usare il token come header `Authorization: Bearer <token>` per tutte le altre richieste

### Esportazione dati

- `/export/{entita}?formato=csv|json` (solo admin)
- Entità supportate: utenti, locations, oggetti, attivita, note

### CORS

CORS abilitato per tutte le origini (in sviluppo). In produzione si consiglia di restringere.

## Test automatici

- Test CRUD di base sulle API REST: `pytest test_api.py`
- Richiede dipendenze: `pytest`, `httpx`

---

## 📚 Documentazione e risorse

- [Piano di lavoro e avanzamento](./PIANO_LAVORO.md)
- [Pianificazione modalità database (server/browser)](./PIANIFICAZIONE_MODALITA_DB.md)
- [Test CRUD automatici (script)](./test_crud.py)
- [Test automatici API REST (pytest)](./test_api.py)
- [Script creazione DB MariaDB](./createdb-mariadb.sql)
- [Script creazione DB PostgreSQL](./createdb-pg.sql)
- [Script creazione DB SQLite](./createdb-sqlite.sql)

---

## Navigazione rapida

- [Funzionalità principali](#-funzionalità-principali)
- [Requisiti](#️-requisiti)
- [Installazione](#-installazione)
- [Struttura del progetto](#-struttura-del-progetto)
- [Configurazione multi-database](#️-configurazione-multi-database)
- [Test CRUD automatici](#-test-crud-automatici)
- [API REST](#api-rest)
- [Test automatici](#test-automatici)

## Sicurezza e best practice

- In produzione, imposta la variabile d'ambiente `CORS_ORIGINS` con i domini autorizzati (es: `CORS_ORIGINS=https://boxboard.example.com`)
- Non lasciare mai CORS aperto (`*`) in produzione!
- Usa password robuste e aggiorna regolarmente le dipendenze.
- Proteggi il file `.env` e non committare mai segreti o credenziali.
- Consulta la sezione 'Roadmap avanzata' in [PIANO_LAVORO.md](./PIANO_LAVORO.md) per ulteriori best practice.

## CI/CD (Integrazione e Deploy Continui)

BoxBoard utilizza **GitHub Actions** per automatizzare i test e garantire la qualità del codice ad ogni push o pull request.

### Come funziona la pipeline
- Il workflow si trova in `.github/workflows/ci.yml`.
- Ad ogni push o PR su `main`, vengono eseguiti:
  - **Installazione dipendenze** (requirements.txt)
  - **Linting** con flake8 (verifica stile e qualità del codice Python)
  - **Test automatici API** (`pytest test_api.py`)
  - **Test CRUD automatici** (`python test_crud.py`)
- Il badge di stato build/test è visibile in alto nel README.

### Come abilitare i workflow GitHub
- Per poter pushare o aggiornare i workflow (`.github/workflows/ci.yml`), il token usato deve avere il permesso `workflow`.
- Se ricevi errori di push relativi ai workflow, aggiorna il token oppure modifica i workflow direttamente da GitHub web.

### Personalizzazione e best practice
- Puoi aggiungere badge personalizzati (coverage, lint, deploy) seguendo la documentazione di GitHub Actions.
- In produzione, aggiungi step per:
  - Deploy automatico (es. su server, Docker, Streamlit Cloud)
  - Notifiche (Slack, email, Telegram)
  - Analisi di sicurezza (Bandit, Snyk)
- Mantieni i segreti (token, password) solo in GitHub Secrets, **mai nel codice**.

### Esempio di estensione pipeline
Per aggiungere il deploy automatico dopo i test:
```yaml
- name: Deploy su server
  run: |
    scp -r . user@server:/path/to/app
    ssh user@server 'cd /path/to/app && docker-compose up -d'
  if: github.ref == 'refs/heads/main' && success()
```

Consulta la documentazione ufficiale [GitHub Actions](https://docs.github.com/it/actions) per tutte le possibilità di automazione.

## Gestione segreti e variabili di ambiente

- Usa il file `.env.example` come riferimento e **non committare mai il file `.env` reale**.
- In sviluppo puoi usare `python-dotenv` per caricare le variabili da `.env`.
- In produzione usa sistemi di secret management (GitHub Secrets, Docker secrets, variabili ambiente del server, ecc.).
- Imposta sempre una `API_SECRET_KEY` robusta e non lasciarla mai vuota in produzione.
- Consulta la sezione sicurezza per altre best practice.

## Sincronizzazione dati browser/server

BoxBoard permette di sincronizzare manualmente i dati tra la modalità browser (locale) e il backend server tramite API REST.

### Come funziona
- In modalità browser puoi esportare i dati in JSON e importarli nel server tramite gli endpoint `/import-bulk/{entita}` (solo admin).
- Puoi anche scaricare i dati dal server tramite `/export-bulk/{entita}` e importarli nel browser.
- I pulsanti di sincronizzazione sono disponibili nell'interfaccia browser (sezione CRUD locale).

### Attenzione e limiti
- La sincronizzazione è **manuale**: l'utente deve esportare/importare i dati quando desidera.
- In caso di dati diversi tra browser e server, l'importazione sovrascrive/aggiorna i record con lo stesso ID.
- **Conflitti**: se lo stesso record è stato modificato sia su browser che su server, l'ultimo import prevale (non c'è merge automatico).
- Si consiglia di esportare sempre una copia di backup prima di importare dati.
- In futuro sarà possibile implementare una sincronizzazione automatica e gestione avanzata dei conflitti.

## Modalità browser (CRUD locale con Dexie.js)

Per abilitare la modalità solo-browser:

1. Includi Dexie.js nel tuo HTML:
   ```html
   <script src="https://unpkg.com/dexie@3.2.4/dist/dexie.min.js"></script>
   ```
2. Includi il file `streamlit_components/crud_browser_frontend.js` fornito nel repo.
3. Collega i pulsanti HTML alle funzioni JS (esempi):
   ```html
   <button onclick="exportAll()">Esporta dati</button>
   <button onclick="importAll(prompt('Incolla JSON'))">Importa dati</button>
   <button onclick="syncUpload('oggetti', 'https://TUO_API_URL', 'TOKEN')">Sync upload oggetti</button>
   <button onclick="syncDownload('oggetti', 'https://TUO_API_URL', 'TOKEN')">Sync download oggetti</button>
   ```
4. Consulta i commenti nel file JS per dettagli su CRUD, esportazione/importazione e sincronizzazione manuale.

**Nota:** Nessuna installazione o build è richiesta su questo sistema. Testa la logica in ambiente browser reale.
