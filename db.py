import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,              -- YYYY-MM-DD
    tipo TEXT NOT NULL               -- 'push', 'pull', 'legs', 'full'
);

CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id INTEGER NOT NULL REFERENCES sessoes(id),
    exercicio TEXT NOT NULL,
    reps INTEGER NOT NULL,
    carga REAL NOT NULL,             -- kg
    rpe REAL,                        -- 1-10, opcional
    serie_num INTEGER                -- ordem dentro do exercício
);

CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,         -- 'ganhar 2kg de massa em 8 semanas'
    ativa INTEGER DEFAULT 1
);
"""

def conectar(caminho="treinos.db"):
    conn = sqlite3.connect(caminho)
    conn.executescript(SCHEMA)
    conn.row_factory = sqlite3.Row
    return conn