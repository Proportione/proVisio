"""Control 3 — bitácora append-only a nivel de aplicación (FEDS C4/C2; C5 NO reclamado).

Deriva de `aggregator._log_evidence` del wallboard, pero **ENCENDIDA por defecto** en
el artefacto (en producción está OFF salvo config). Registra, una fila por evento y
en orden de llegada:
  - transiciones de alerta (levantada/despejada) — condiciones operativas surgidas.
  - afirmaciones de fusión emitidas — corpus auditable para Componente B.
JSONL append-only: crece sola (C2, corre desatendido), es evidencia de qué sacó a la
luz el artefacto (C4). C5 no se reclama en la final version del paper. Los errores de E/S se
tragan: la evidencia NUNCA debe tumbar el board.
"""

import json
from pathlib import Path

# provisio/gobernanza/audit_trail.py -> .../provisio-artifact/evaluacion/audit-log.jsonl
DEFAULT_PATH = Path(__file__).resolve().parents[2] / "evaluacion" / "audit-log.jsonl"


def append(rows, path=None):
    """Anexa filas (dicts) a la bitácora. Best-effort: no lanza."""
    if not rows:
        return
    p = Path(path or DEFAULT_PATH)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except OSError:
        pass


def log_fusion(fusion, ts, path=None):
    """Registra las afirmaciones de una fusión como filas de corpus (Componente B)."""
    r = (fusion or {}).get("brazo_R") or {}
    rows = [{
        "ts": ts, "event": "fusion_claim", "fusion": fusion.get("id"),
        "brazo": "R", "texto": a.get("texto"), "citas": a.get("citas"),
    } for a in r.get("afirmaciones", [])]
    l = (fusion or {}).get("brazo_L") or {}
    if l.get("sintesis"):
        rows.append({"ts": ts, "event": "fusion_claim", "fusion": fusion.get("id"),
                     "brazo": "L", "texto": l.get("sintesis"), "citas": l.get("citas"),
                     "modelo": l.get("modelo")})
    append(rows, path)
    return rows
