# Piano di Lavoro per il Recupero e Completamento di BoxBoard

Questo documento elenca i passi da seguire per rendere il progetto coerente, manutenibile e realmente multi-database. Ogni punto verrà spuntato al completamento.

---

## Fase 1: Fondamenta e coerenza
- [ ] **Separazione della configurazione**
  - Creare un file `.env` o `config.py` per gestire i parametri di connessione (tipo di database, host, user, password, nome DB, ecc.).
  - Modificare `app.py` per leggere la configurazione da questo file.

- [ ] **Astrazione del database**
  - Creare un modulo (es. `db.py`) che gestisca la connessione e le query in modo astratto, scegliendo il driver giusto in base al tipo di database.
  - Opzionale: valutare l'uso di **SQLAlchemy** per semplificare la compatibilità tra DBMS.

- [ ] **Refactoring del codice**
  - Modificare tutte le funzioni di accesso al database in `app.py` per usare il nuovo modulo di astrazione.
  - Garantire che le query siano compatibili con tutti i DB supportati (MariaDB/MySQL, PostgreSQL, SQLite).

---

## Fase 2: Robustezza e usabilità
- [ ] **Gestione degli errori e messaggi chiari**
  - Migliorare la gestione delle eccezioni e fornire messaggi d'errore utili all'utente.

- [ ] **Aggiornamento della documentazione**
  - Aggiornare il `README.md` con istruzioni chiare su come configurare e scegliere il database.
  - Spiegare come aggiungere nuovi DBMS in futuro.

- [ ] **Aggiunta di dati di esempio e test**
  - Fornire una funzione/script per popolare il database con dati di esempio.
  - (Opzionale) Aggiungere test automatici per le funzioni principali.

---

## Fase 3: Migliorie e manutenzione
- [ ] **Pulizia e ottimizzazione del codice**
  - Rimuovere codice duplicato, commenti inutili, variabili hardcoded.
  - Migliorare la struttura delle funzioni e la leggibilità.

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