from db import conectar

def epley_1rm(carga, reps):
    """1RM estimado pela fórmula de Epley."""
    return carga * (1 + reps / 30)

def resumo_exercicio(conn, exercicio, ultimas_n=6):
    rows = conn.execute("""
        SELECT s.data, se.reps, se.carga, se.rpe
        FROM series se JOIN sessoes s ON s.id = se.sessao_id
        WHERE se.exercicio = ?
        ORDER BY s.data DESC
        LIMIT ?
    """, (exercicio, ultimas_n * 10)).fetchall()
    if not rows:
        return None
    por_data = {}
    for r in rows:
        d = r["data"]
        por_data.setdefault(d, {"volume": 0, "1rm_max": 0, "rpe_medio": []})
        por_data[d]["volume"] += r["carga"] * r["reps"]
        por_data[d]["1rm_max"] = max(por_data[d]["1rm_max"],
                                     epley_1rm(r["carga"], r["reps"]))
        if r["rpe"]:
            por_data[d]["rpe_medio"].append(r["rpe"])
    datas = sorted(por_data.keys())
    return {
        "exercicio": exercicio,
        "sessoes": [
            {"data": d,
             "volume": round(por_data[d]["volume"], 1),
             "1rm_estimado": round(por_data[d]["1rm_max"], 1),
             "rpe_medio": round(sum(por_data[d]["rpe_medio"]) /
                                len(por_data[d]["rpe_medio"]), 1)
                            if por_data[d]["rpe_medio"] else None}
            for d in datas
        ],
    }

def resumo_geral(conn, dias=28):
    exercicios = [r[0] for r in conn.execute(
        "SELECT DISTINCT exercicio FROM series").fetchall()]
    return [resumo_exercicio(conn, ex) for ex in exercicios]