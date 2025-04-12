import sqlite3

def inicializar_banco():
    conn = sqlite3.connect("rastreamento.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_serie TEXT NOT NULL,
        ordem_producao TEXT NOT NULL,
        modelo_placa TEXT NOT NULL,
        linha_producao TEXT NOT NULL CHECK(linha_producao IN ('SMT1-01', 'SMT3-004', 'SMT3-01', 'SMT3-02', 'SMT3-03', 'SMT3-05', 'Desconhecida')),
        data_hora TEXT DEFAULT CURRENT_TIMESTAMP,
        operador TEXT NOT NULL,
        turno TEXT NOT NULL,
        fase TEXT NOT NULL,
        status TEXT DEFAULT 'Aprovada' NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reprovacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_serie TEXT,
        ordem_producao TEXT,
        modelo_placa TEXT,
        linha_producao TEXT,
        operador TEXT,
        turno TEXT,
        data_hora TEXT,
        motivo TEXT,
        status TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        matricula TEXT NOT NULL UNIQUE
    )
    ''')

    # Insere usuários de teste
    usuarios = [("Operador 1", "12345"), ("Operador 2", "67890")]
    for nome, matricula in usuarios:
        cursor.execute("INSERT OR IGNORE INTO usuarios (nome, matricula) VALUES (?, ?)", (nome, matricula))

    conn.commit()
    conn.close()
