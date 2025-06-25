# BoxBoard – Guida Rapida Utente

Benvenuto in **BoxBoard**, la soluzione open source per la gestione di oggetti, attività e contenitori in scenari di svuotamento cantine, magazzini o archiviazione!

---

## Indice
- [Cos'è BoxBoard](#cosè-boxboard)
- [Installazione e Avvio](#installazione-e-avvio)
- [Primo Accesso e Login](#primo-accesso-e-login)
- [Panoramica Dashboard](#panoramica-dashboard)
- [Gestione Oggetti, Attività, Note](#gestione-oggetti-attività-note)
- [Modalità Server e Browser](#modalità-server-e-browser)
- [Sincronizzazione dati](#sincronizzazione-dati)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)

---

## Cos'è BoxBoard
BoxBoard è una webapp moderna, multi-database, con interfaccia intuitiva e dashboard avanzata, pensata per:
- Tracciare oggetti, contenitori, attività e note
- Gestire utenti e ruoli
- Lavorare sia online (server) che offline (browser)
- Esportare/importare e sincronizzare dati facilmente

---

## Installazione e Avvio

1. **Clona il repository**
   ```bash
   git clone https://github.com/amaigit/boxboard.git
   cd boxboard
   ```
2. **Crea ambiente virtuale e installa dipendenze**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configura il database**
   - Copia `.env.example` in `.env` e personalizza i parametri
   - Avvia il database scelto (MariaDB, PostgreSQL, SQLite)
4. **Avvia l'applicazione**
   ```bash
   streamlit run app.py
   ```
5. **(Opzionale) Modalità browser**
   - Apri l'app e scegli "Modalità browser" dal pannello laterale per lavorare solo localmente

---

## Primo Accesso e Login
- All'avvio viene richiesto il login (username = email, password = impostata dall'admin)
- Solo utenti autenticati possono accedere alle funzionalità
- Gli admin possono gestire utenti e ruoli dalla sezione dedicata

---

## Panoramica Dashboard

La dashboard offre:
- **Statistiche rapide**: utenti, location, oggetti, attività pendenti
- **Filtri avanzati**: ricerca full-text, filtri per utente e stato
- **Attività per utente**: tabella filtrabile
- **Attività urgenti**: scadenze imminenti
- **Oggetti più movimentati**: top 5
- **Storico modifiche recenti**: log delle ultime operazioni

Naviga tra le sezioni dal menu laterale: Utenti, Location, Oggetti, Attività, Note, Statistiche.

---

## Gestione Oggetti, Attività, Note
- **Oggetti**: aggiungi, modifica, filtra per location, stato, tipo, contenitore
- **Attività**: crea, assegna, completa attività su oggetti
- **Note**: aggiungi note a oggetti, attività o location
- **Tutto è tracciato nel log operazioni**

---

## Modalità Server e Browser

- **Server**: dati condivisi, multiutente, backup, accesso remoto
- **Browser**: dati solo locali, privacy totale, uso offline, nessun server richiesto
- Puoi esportare/importare dati tra le due modalità (JSON)
- Scegli la modalità dal pannello laterale all'avvio

---

## Sincronizzazione dati

- **Manuale**: esporta dati in JSON e importa su server/browser tramite pulsanti dedicati
- **Automatica**: in modalità browser, la sincronizzazione avviene anche in automatico quando torni online (se configurato)
- **Attenzione**: in caso di conflitti, l'ultimo import prevale

---

## FAQ

**1. Non riesco ad accedere, cosa posso fare?**
- Verifica username/email e password
- Chiedi all'admin di resettare la password

**2. Come posso cambiare modalità (server/browser)?**
- Dal pannello laterale, scegli la modalità desiderata

**3. Come faccio il backup dei dati?**
- Usa il pulsante "Esporta dati" per scaricare un file JSON di backup

**4. Posso usare BoxBoard offline?**
- Sì, scegli la modalità browser per lavorare offline

**5. Come risolvo conflitti tra dati server e browser?**
- Prima di importare, esporta sempre una copia di backup
- In caso di conflitto, l'ultimo import sovrascrive i dati

**6. Come aggiungo nuovi utenti?**
- Solo gli admin possono aggiungere/modificare utenti dalla sezione "Utenti"

**7. Come aggiorno BoxBoard?**
- Esegui `git pull` e aggiorna le dipendenze con `pip install -r requirements.txt`

---

## Troubleshooting

- **Errore di connessione al database**: verifica i parametri in `.env` e che il DB sia attivo
- **Problemi di permessi**: assicurati di avere i ruoli corretti
- **Dati non visibili in modalità browser**: controlla che Dexie.js sia incluso e che il browser supporti IndexedDB
- **Problemi di sincronizzazione**: esporta sempre un backup prima di importare, verifica la connessione

---

Per ulteriori dettagli consulta la [documentazione completa](./README.md) o apri una issue su GitHub! 