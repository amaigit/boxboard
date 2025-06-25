DROP SCHEMA IF EXISTS svuotacantine CASCADE;
CREATE SCHEMA svuotacantine;
SET search_path TO svuotacantine;

-- UTENTI
CREATE TABLE utenti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ruolo VARCHAR(20) CHECK (ruolo IN ('Operatore', 'Coordinatore', 'Altro')) DEFAULT 'Operatore',
    email VARCHAR(100) UNIQUE
);

-- LOCATION
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    indirizzo VARCHAR(255),
    note TEXT,
    data_creazione TIMESTAMP DEFAULT NOW()
);

-- OGGETTI (con contenitore self-reference)
CREATE TABLE oggetti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT,
    stato VARCHAR(20) CHECK (stato IN ('da_rimuovere', 'smaltito', 'venduto', 'in_attesa', 'completato')) DEFAULT 'da_rimuovere',
    tipo VARCHAR(20) CHECK (tipo IN ('oggetto', 'contenitore')) DEFAULT 'oggetto',
    location_id INT REFERENCES locations(id) ON DELETE SET NULL,
    contenitore_id INT REFERENCES oggetti(id) ON DELETE SET NULL,
    data_rilevamento TIMESTAMP DEFAULT NOW()
);

-- ATTIVITA
CREATE TABLE attivita (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT
);

-- OGGETTO_ATTIVITA
CREATE TABLE oggetto_attivita (
    id SERIAL PRIMARY KEY,
    oggetto_id INT NOT NULL REFERENCES oggetti(id) ON DELETE CASCADE,
    attivita_id INT NOT NULL REFERENCES attivita(id) ON DELETE CASCADE,
    completata BOOLEAN DEFAULT FALSE,
    data_prevista DATE,
    data_completamento DATE,
    assegnato_a INT REFERENCES utenti(id)
);

-- NOTE
CREATE TABLE note (
    id SERIAL PRIMARY KEY,
    testo TEXT NOT NULL,
    oggetto_id INT REFERENCES oggetti(id) ON DELETE CASCADE,
    attivita_id INT REFERENCES attivita(id) ON DELETE CASCADE,
    location_id INT REFERENCES locations(id) ON DELETE CASCADE,
    autore_id INT REFERENCES utenti(id),
    data TIMESTAMP DEFAULT NOW()
);

-- LOG OPERAZIONI
CREATE TABLE IF NOT EXISTS log_operazioni (
    id SERIAL PRIMARY KEY,
    utente_id INT NOT NULL REFERENCES utenti(id),
    azione VARCHAR(50) NOT NULL,
    entita VARCHAR(50) NOT NULL,
    entita_id INT,
    dettagli TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
