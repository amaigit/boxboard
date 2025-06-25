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

   * Per MariaDB:

     ```bash
     mysql -u root -p < createdb-mariadb.sql
     ```

   * Per PostgreSQL:

     ```bash
     psql -U postgres -f createdb-pg.sql
     ```

   * Per SQLite:

     ```bash
     sqlite3 boxboard.db < createdb-sqlite.sql
     ```

5. Avvia l'app:

   ```bash
   streamlit run app.py
   ```

---

## 📄 Struttura del progetto

```
boxboard/
├── app.py                  # Codice principale dell'app Streamlit
├── createdb-mariadb.sql    # Script di creazione del database per MariaDB
├── createdb-pg.sql         # Script di creazione del database per PostgreSQL
├── createdb-sqlite.sql     # Script di creazione del database per SQLite
├── requirements.txt        # Dipendenze del progetto
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
