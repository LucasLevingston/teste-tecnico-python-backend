from get_conn import get_conn


def diagnostico_produtividade():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM registros")
    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    if total == 0:
        return {
            "media_nivel_foco": None,
            "tempo_total_minutos": 0,
            "registros": 0,
            "mensagem": "Nenhum registro encontrado. Comece registrando uma sessão com POST /registro-foco",
            "top_categorias_por_tempo": [],
        }

    soma_foco = sum(row["nivel_foco"] for row in rows)
    soma_tempo = sum(row["tempo_minutos"] for row in rows)
    media = round(soma_foco / total, 2)

    if media >= 4.5:
        mensagem = "Você está em uma maratona produtiva de alto nível! Mantenha o ritmo e cuide do descanso."
    elif media >= 4.0:
        mensagem = "Ótimo foco! Continue com boas práticas e pequenas pausas."
    elif media >= 3.0:
        mensagem = "Produtividade razoável — experimente técnicas Pomodoro e minimize interrupções."
    elif media >= 2.0:
        mensagem = "Médio-baixo. Tente reduzir distrações e planejar blocos maiores de trabalho."
    else:
        mensagem = "Nível de foco baixo. Pausas estruturadas, bloquear notificações e revisar objetivos podem ajudar."

    categorias = {}
    for row in rows:
        cat = row["categoria"] or "outros"
        categorias[cat] = categorias.get(cat, 0) + row["tempo_minutos"]

    top_categorias = sorted(categorias.items(), key=lambda x: x[1], reverse=True)
    top_categorias_list = [{"categoria": c, "tempo_minutos": t} for c, t in top_categorias]

    return {
        "media_nivel_foco": media,
        "tempo_total_minutos": soma_tempo,
        "registros": total,
        "mensagem": mensagem,
        "top_categorias_por_tempo": top_categorias_list,
    }
