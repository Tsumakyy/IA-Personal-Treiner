import argparse
from datetime import date
from db import conectar

def registrar(data, tipo, exercicios):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO sessoes (data, tipo) VALUES (?, ?)", (data, tipo))
    sessao_id = cur.lastrowid
    for ex in exercicios:
        # formato: "supino,3,8,80,8"  -> nome,series,reps,carga,rpe
        nome, n_series, reps, carga, rpe = ex.split(",")
        for i in range(1, int(n_series) + 1):
            cur.execute(
                "INSERT INTO series (sessao_id, exercicio, reps, carga, rpe, serie_num) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (sessao_id, nome, int(reps), float(carga), float(rpe), i),
            )
    conn.commit()
    conn.close()
    print(f"✅ Sessão {tipo} de {data} registrada com {len(exercicios)} exercícios.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=date.today().isoformat())
    p.add_argument("--tipo", required=True)
    p.add_argument("--ex", nargs="+", required=True,
                   help="formato: nome,series,reps,carga,rpe")
    args = p.parse_args()
    registrar(args.data, args.tipo, args.ex)