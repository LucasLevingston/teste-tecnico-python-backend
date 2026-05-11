from datetime import datetime
from fastapi import HTTPException
from get_conn import get_conn
from models import RegistroIn
from normalize_tags import normalize_tags


def criar_registro(r: RegistroIn):
    if not r.comentario or not r.comentario.strip():
        raise HTTPException(status_code=400, detail="Campo 'comentario' não pode ser vazio")

    tags_str = normalize_tags(r.tags)

    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO registros (nivel_foco, tempo_minutos, comentario, categoria, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (r.nivel_foco, r.tempo_minutos, r.comentario.strip(), r.categoria, tags_str, now),
    )
    conn.commit()
    last_id = cur.lastrowid
    conn.close()

    return {
        "id": last_id,
        "nivel_foco": r.nivel_foco,
        "tempo_minutos": r.tempo_minutos,
        "comentario": r.comentario.strip(),
        "categoria": r.categoria,
        "tags": r.tags,
        "created_at": now,
    }
