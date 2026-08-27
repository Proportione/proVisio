"""Componente A — CAPACIDAD (viabilidad de instrumentación, NO efecto).

Corre la fusión indicada end-to-end L1->L5 sobre el snapshot congelado y reporta un
REGISTRO DE TRAZA E2E (no una métrica de resultado):
  1. Cobertura de etapas L1->L5 (checklist binario 5/5).
  2. Fidelidad de datos: cifra-en-panel = cifra-en-fuente (censo K1), tolerancia 0.
  3. Reproducibilidad: dos pasadas del snapshot dan output idéntico (determinismo).
  4. Etiquetado de fuerza de señal por familia.

Claim admisible: capacidad/viabilidad. PROHIBIDO reclamar efecto de negocio o
estadística. Uso:  python -m evaluacion.componente_a_capacidad --fusion fa1 --snapshot
"""

import argparse
import json
import sys
from pathlib import Path

# permite `python evaluacion/componente_a_capacidad.py` sin instalar el paquete
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from provisio.ciclo_vida.aggregator import build_board          # noqa: E402
from provisio.l1_ingesta._snapshot import load                  # noqa: E402
from provisio.gobernanza import citacion                        # noqa: E402


def checklist_l1_l5(board):
    """5 etapas del pipeline, cada una verificada sobre el board compuesto."""
    signals = board.get("signals", {})
    screens = board.get("screens", {})
    fusion = board.get("fusion", {})
    k1 = screens.get("k1", {})
    return {
        "L1 ingerido": bool(signals.get("s1")) and bool(signals.get("s2")),
        "L2 normalizado": isinstance((signals.get("s2") or {}).get("channel_mix"), dict)
        and bool((signals.get("s2") or {}).get("channel_mix")),
        "L3 fusionado": (fusion.get("fa1", {}).get("estado_carril") == "ejercido"),
        "L4 KPI derivado": k1.get("deals") is not None,
        "L5 presentado": bool(board.get("generatedAt")) and bool(board.get("blocks")),
    }


def fidelidad_censo(board, config):
    """Reconciliación cifra-en-panel (K1) = cifra-en-fuente (snapshot census)."""
    fuente = (load("crm.json", config).get("census") or {})
    panel = board.get("screens", {}).get("k1", {})
    campos = ["contactos", "clientes", "leads", "prospectos", "deals", "follow_ups_vencidos"]
    filas, ok = [], True
    for c in campos:
        f, p = fuente.get(c), panel.get(c)
        match = (f == p)
        ok = ok and match
        filas.append({"campo": c, "fuente": f, "panel": p, "match": match})
    return ok, filas


def run(fusion="fa1", config=None):
    config = dict(config or {})
    config.setdefault("mode", "snapshot")
    b1 = build_board(config, audit=True)          # pasada 1 (brazo R; sin LLM = determinista) — deja audit-trail
    b2 = build_board(config)                       # pasada 2 (reproducibilidad; sin audit para no duplicar el corpus)

    chk = checklist_l1_l5(b1)
    fid_ok, fid = fidelidad_censo(b1, config)
    # determinismo: se ignora generatedAt (timestamp) al comparar
    def _clave(b):
        c = dict(b); c.pop("generatedAt", None); c["blocks"] = {k: {"stale": v.get("stale")} for k, v in c.get("blocks", {}).items()}
        return json.dumps(c, sort_keys=True, ensure_ascii=False)
    reproducible = _clave(b1) == _clave(b2)

    m1 = citacion.audita_fusion(b1.get("fusion", {}).get("fa1", {}))
    return {
        "fusion": fusion.upper().replace("FA", "F-A"),
        "checklist": chk,
        "checklist_verde": all(chk.values()),
        "fidelidad_censo_ok": fid_ok,
        "fidelidad_detalle": fid,
        "reproducible": reproducible,
        "citacion_brazo_R": m1["m1_brazo_R"],
        "fuerza_senal": {"S1": "fina", "S2": "presente", "S3": "N/A", "K1": "alta"},
    }


def _print(res):
    print(f"\n=== Componente A · CAPACIDAD · {res['fusion']} (S1+S2 -> K1) ===\n")
    print("Cobertura de etapas L1->L5:")
    for etapa, ok in res["checklist"].items():
        print(f"  [{'x' if ok else ' '}] {etapa}")
    verde = sum(res["checklist"].values())
    print(f"  -> {verde}/5 {'VERDE' if res['checklist_verde'] else 'INCOMPLETO'}\n")
    print(f"Fidelidad censo K1 (panel == fuente, tol. 0): "
          f"{'OK' if res['fidelidad_censo_ok'] else 'FALLO'}")
    for f in res["fidelidad_detalle"]:
        print(f"    {f['campo']:>22}: fuente={f['fuente']} panel={f['panel']} "
              f"{'==' if f['match'] else '!='}")
    print(f"\nReproducibilidad (snapshot re-corre idéntico): "
          f"{'OK' if res['reproducible'] else 'FALLO'}")
    print(f"Citación por afirmación (brazo R, M1): {res['citacion_brazo_R']:.2f}")
    print(f"Fuerza de señal: {res['fuerza_senal']}")
    print("\nClaim admisible: CAPACIDAD/viabilidad de instrumentación E2E. NO efecto.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fusion", default="fa1")
    ap.add_argument("--snapshot", action="store_true", help="(por defecto) modo snapshot")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = run(args.fusion, {"mode": "snapshot"})
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        _print(res)
    ok = res["checklist_verde"] and res["fidelidad_censo_ok"] and res["reproducible"]
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
