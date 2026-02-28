-- EY EY EY ESKEMA HEMEN DAGO EY EY EY

PRAGMA foreign_keys = ON; -- FK AKTIBATZEKO

-- =========================
-- TABLE: trigger
-- =========================
CREATE TABLE trigger (
    idTrigger INTEGER PRIMARY KEY AUTOINCREMENT,
    content   TEXT NOT NULL
);

-- =========================
-- TABLE: response
-- =========================
CREATE TABLE response (
    idResponse INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT NOT NULL
);

-- =========================
-- TABLE: combo
-- Many-to-many 
-- TRIGGER bakoitzeko hainbat response, trigger desberdinek response bera izan dezakete
-- =========================
CREATE TABLE combo (
    idCombo     INTEGER PRIMARY KEY AUTOINCREMENT,
    idTrigger   INTEGER NOT NULL,
    idResponse  INTEGER NOT NULL,

    FOREIGN KEY (idTrigger)
        REFERENCES trigger(idTrigger)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (idResponse)
        REFERENCES response(idResponse)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Prevent duplicate trigger/response pairings
    UNIQUE (idTrigger, idResponse)
);

CREATE TABLE user (
    id serial primary key,
    username varchar(255) not null,
    password_hash varchar(255) not null
);

CREATE INDEX idx_combo_trigger ON combo(idTrigger);
CREATE INDEX idx_combo_response ON combo(idResponse);

-- =========================
-- TABLE: templates
-- =========================
CREATE TABLE templates (
    idTemplate          INTEGER PRIMARY KEY AUTOINCREMENT,
    templateCommand     varchar(255) NOT NULL,
    templateImageFile   varchar(255) NOT NULL,
    -- Top Left X
    templateTextBoxTLX  INTEGER NOT NULL,
    -- Top Left Y
    templateTextBoxTLY  INTEGER NOT NULL,
    -- Bottom Right X
    templateTextBoxBRX  INTEGER NOT NULL,
    -- Bottom Right Y
    templateTextBoxBRY  INTEGER NOT NULL,
    defaultTextColour   varchar(16) NOT NULL
);