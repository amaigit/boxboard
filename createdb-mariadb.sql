-- CREAZIONE DATABASE
DROP DATABASE IF EXISTS svuotacantine;
CREATE DATABASE svuotacantine DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE svuotacantine;

-- 1. UTENTI
CREATE TABLE utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ruolo ENUM('Operatore', 'Coordinatore', 'Altro') DEFAULT 'Operatore',
    email VARCHAR(100) UNIQUE
);

-- 2. LOCATION
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    indirizzo VARCHAR(255),
    note TEXT,
    data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. OGGETTI (con self-reference per contenitori)
CREATE TABLE oggetti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT,
    stato ENUM('da_rimuovere', 'smaltito', 'venduto', 'in_attesa', 'completato') DEFAULT 'da_rimuovere',
    tipo ENUM('oggetto', 'contenitore') DEFAULT 'oggetto',
    location_id INT,
    contenitore_id INT,
    data_rilevamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (contenitore_id) REFERENCES oggetti(id) ON DELETE SET NULL
);

-- 4. ATTIVITA
CREATE TABLE attivita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT
);

-- 5. OGGETTO_ATTIVITA (relazione N:N + gestione completamento)
CREATE TABLE oggetto_attivita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    oggetto_id INT NOT NULL,
    attivita_id INT NOT NULL,
    completata BOOLEAN DEFAULT FALSE,
    data_prevista DATE,
    data_completamento DATE,
    assegnato_a INT,

    FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
    FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
    FOREIGN KEY (assegnato_a) REFERENCES utenti(id) ON DELETE SET NULL
);

-- 6. NOTE (collegabili a oggetti, attività o location)
CREATE TABLE note (
    id INT AUTO_INCREMENT PRIMARY KEY,
    testo TEXT NOT NULL,
    oggetto_id INT,
    attivita_id INT,
    location_id INT,
    autore_id INT,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (oggetto_id) REFERENCES oggetti(id) ON DELETE CASCADE,
    FOREIGN KEY (attivita_id) REFERENCES attivita(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
    FOREIGN KEY (autore_id) REFERENCES utenti(id) ON DELETE SET NULL
);

-- 7. LOG OPERAZIONI
CREATE TABLE IF NOT EXISTS log_operazioni (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utente_id INT NOT NULL,
    azione VARCHAR(50) NOT NULL,
    entita VARCHAR(50) NOT NULL,
    entita_id INT,
    dettagli TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utente_id) REFERENCES utenti(id) ON DELETE CASCADE
);
