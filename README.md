# BoxBoard

![Boxboard Logo](https://github.com/amaigit/boxboard/raw/main/assets/logo.png)

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
