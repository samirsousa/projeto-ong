-- Tabelas do banco de dados do site (SQLite)
-- "IF NOT EXISTS" faz a tabela ser criada só quando ainda não existe

-- Só existe um administrador ("Só pode haver um")
CREATE TABLE IF NOT EXISTS admin (
    id                INTEGER PRIMARY KEY CHECK (id = 1),
    email             TEXT NOT NULL,
    senha             TEXT NOT NULL,
    senha_alterada_em TEXT
);

-- Posts do Instagram e os Posts removidos continuam aqui para manter histórico
CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    link        TEXT NOT NULL UNIQUE,
    filtro      TEXT NOT NULL,
    formato     TEXT NOT NULL,
    tema        TEXT NOT NULL DEFAULT '',
    legenda     TEXT NOT NULL DEFAULT '',
    hashtags    TEXT NOT NULL DEFAULT '',
    imagem      TEXT NOT NULL DEFAULT '',
    inserido_em TEXT NOT NULL,
    ativo       INTEGER NOT NULL DEFAULT 1,
    removido_em TEXT
);

-- Pessoas da Família AEPEC
CREATE TABLE IF NOT EXISTS equipe (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    cargo         TEXT NOT NULL DEFAULT '',
    area          TEXT NOT NULL DEFAULT '',
    texto         TEXT NOT NULL DEFAULT '',
    posicao       INTEGER NOT NULL,
    atualizado_em TEXT
);

-- Fotos de cada pessoa (duas max)
CREATE TABLE IF NOT EXISTS equipe_fotos (
    membro_id INTEGER NOT NULL REFERENCES equipe (id) ON DELETE CASCADE,
    posicao   INTEGER NOT NULL,
    caminho   TEXT NOT NULL,
    PRIMARY KEY (membro_id, posicao)
);

-- Fotos dos projetos
CREATE TABLE IF NOT EXISTS projeto_fotos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id TEXT NOT NULL,
    posicao    INTEGER NOT NULL,
    caminho    TEXT NOT NULL
);

-- Galeria da página inicial
CREATE TABLE IF NOT EXISTS galeria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    foto        TEXT NOT NULL,
    tipo        TEXT NOT NULL,
    titulo      TEXT NOT NULL DEFAULT '',
    texto       TEXT NOT NULL DEFAULT '',
    posicao     INTEGER NOT NULL,
    inserido_em TEXT NOT NULL
);

-- Tentativas erradas de login (evitar brute force)
CREATE TABLE IF NOT EXISTS tentativas_login (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ip     TEXT NOT NULL,
    quando REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS tentativas_por_ip ON tentativas_login (ip, quando);