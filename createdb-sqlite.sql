PRAGMA foreign_keys = ON;

-- UTENTI
CREATE TABLE utenti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    ruolo TEXT CHECK (ruolo IN ('Operatore', 'Coordinatore', 'Altro')) DEFAULT 'Operatore',
    email TEXT UNIQUE
);

-- LOCATION
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    indirizzo TEXT,
    note TEXT,
    data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- OGGETTI
CREATE TABLE oggetti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descrizione TEXT,
    stato TEXT CHECK (stato IN ('da_rimuovere', 'smaltito', 'venduto', 'in_attesa', 'completato')) DEFAULT 'da_rimuovere',
    tipo TEXT CHECK (tipo IN ('oggetto', 'contenitore')) DEFAULT 'oggetto',
    location_id INTEGER,
    contenitore_id INTEGER,
    data_rilevamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (contenitore_id) REFERENCES oggetti(id) ON DELETE SET NULL
);

-- ATTIVITA
CREATE TABLE attivita (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descrizione TEXT
);

-- OGGETTO_ATTIVITA
CREATE TABLE oggetto_attivita (
    id INTEGER PRIMARY KEY,
    oggetto_id INTEGER NOT NULL,
    attivita_id INTEGER NOT NULL,
    completata INTEGER DEFAULT 0,
    data_prevista DATE,
    data_completamento DATE,
    assegnato_a INTEGER,
    FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
    FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
    FOREIGN KEY (assegnato_a) REFERENCES utenti(id)
);

-- NOTE
CREATE TABLE note (
    id INTEGER PRIMARY KEY,
    testo TEXT NOT NULL,
    oggetto_id INTEGER,
    attivita_id INTEGER,
    location_id INTEGER,
    autore_id INTEGER,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
    FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
    FOREIGN KEY (autore_id) REFERENCES utenti(id)
);

-- LOG OPERAZIONI
CREATE TABLE IF NOT EXISTS log_operazioni (
    id INTEGER PRIMARY KEY,
    utente_id INTEGER NOT NULL,
    azione TEXT NOT NULL,
    entita TEXT NOT NULL,
    entita_id INTEGER,
    dettagli TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utente_id) REFERENCES utenti(id)
);
