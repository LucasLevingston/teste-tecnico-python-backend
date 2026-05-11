from get_conn import get_conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel_foco INTEGER NOT NULL,
            tempo_minutos INTEGER NOT NULL,
            comentario TEXT NOT NULL,
            categoria TEXT,
            tags TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
