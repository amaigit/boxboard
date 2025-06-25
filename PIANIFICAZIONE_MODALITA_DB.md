# Pianificazione: Modalità Database (Server/Browser)

## Obiettivo
Consentire all'utente di scegliere, tramite un pannello frontend, se:
- Collegarsi a un database server-side (MariaDB, PostgreSQL, SQLite, anche remoto)
- Gestire tutti i dati solo nel browser (modalità locale/privata, senza invio dati al server)

---

## Requisiti funzionali
- Pannello impostazioni accessibile dal frontend (Streamlit)
- Scelta tra:
  - Modalità **Server** (come ora, con configurazione DB)
  - Modalità **Browser** (dati solo locali, persistenti nel browser)
- Chiarezza per l'utente su vantaggi/limiti di ciascuna modalità
- Possibilità di esportare/importare dati tra le due modalità (opzionale)

---

## Architettura proposta

### Modalità Server
- Funziona come ora: CRUD tramite SQLAlchemy su DB configurato in `.env` o da pannello.
- Supporto a MariaDB, PostgreSQL, SQLite (anche remoto).

### Modalità Browser
- Utilizzo di **IndexedDB** o **sql.js** (SQLite in WebAssembly) per la persistenza locale nel browser.
- Implementazione di un **Streamlit Component custom**:
  - Espone API JS per CRUD locale
  - Comunica con Python solo per la UI, non per i dati
- Tutte le operazioni CRUD avvengono in JS/browser, i dati non lasciano mai il client.

### Pannello impostazioni
- Pagina Streamlit dedicata (o sidebar) per:
  - Selezionare la modalità
  - Configurare parametri DB (host, user, ecc.) se in modalità server
  - Visualizzare stato e avvisi (es. "Dati solo su questo browser")
  - (Opzionale) Esportare/importare dati (JSON, file SQLite, ecc.)

---

## Vantaggi e limiti

### Modalità Server
- Pro: dati condivisi, multiutente, backup, accesso remoto
- Contro: richiede connessione, gestione server, privacy limitata

### Modalità Browser
- Pro: privacy totale, uso offline, demo, nessun server richiesto
- Contro: dati non condivisi tra dispositivi, rischio perdita dati se si cancella la cache/browser

---

## Roadmap di sviluppo (futura)
1. Progettazione UX pannello impostazioni
2. Implementazione Streamlit Component per CRUD locale (IndexedDB/sql.js)
3. Integrazione logica di scelta modalità e fallback
4. Esportazione/importazione dati (opzionale)
5. Test cross-browser e documentazione

---

## Note
- L'implementazione richiederà competenze sia Python/Streamlit che JavaScript/WebAssembly.
- La modalità browser è ideale per privacy, demo, uso offline, ma non per collaborazione.
- La scelta della modalità deve essere chiara e reversibile per l'utente.

---

**L'effettivo sviluppo verrà affrontato in futuro secondo le priorità del progetto.** 