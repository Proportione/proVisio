"""Alertas — brazo R en vivo (reglas P0/P1 deterministas, ISA-18.2) + transiciones.

`derive_alerts` porta la semántica de condición-EN-VIVO del wallboard (no evento),
reencuadrada al board del artefacto (Incremento 1: familia K1). `alert_transitions`
es VERBATIM del wallboard: diff de alertas entre dos board sucesivos -> filas de
evidencia para la bitácora append-only (gobernanza/audit_trail).
"""


def derive_alerts(board):
    """Reglas sobre el board ya compuesto. Devuelve lista de alerts. Pura."""
    alerts = []
    screens = board.get("screens", {}) or {}
    blocks = board.get("blocks", {}) or {}
    k1 = screens.get("k1", {}) or {}

    # bloque de señal stale (host/fuente inalcanzable) -> el board no se refresca
    for name, blk in blocks.items():
        if (blk or {}).get("stale"):
            alerts.append({
                "id": f"block-stale-{name}", "severity": "P1",
                "title": "Fuente sin refrescar", "detail": f"El bloque '{name}' está stale",
                "source": name,
            })

    # P1: higiene de follow-ups (K1) — condición accionable del funnel real
    vencidos = k1.get("follow_ups_vencidos")
    if isinstance(vencidos, int) and vencidos > 0:
        alerts.append({
            "id": "followups-vencidos", "severity": "P1",
            "title": "Follow-ups vencidos",
            "detail": f"{vencidos} follow-up(s) de deal vencido(s)", "source": "op_crm",
        })
    return alerts


def alert_transitions(prev, new, ts):
    """Diff de alertas entre dos board sucesivos -> filas de evidencia. Pura.
    VERBATIM de wallboard/aggregator.alert_transitions."""
    prev_by_id = {a.get("id"): a for a in (prev or [])}
    new_by_id = {a.get("id"): a for a in (new or [])}
    rows = []
    for i in new_by_id.keys() - prev_by_id.keys():
        a = new_by_id[i]
        rows.append({"ts": ts, "event": "raised", "id": i, "severity": a.get("severity"),
                     "title": a.get("title"), "source": a.get("source")})
    for i in prev_by_id.keys() - new_by_id.keys():
        a = prev_by_id[i]
        rows.append({"ts": ts, "event": "cleared", "id": i, "severity": a.get("severity"),
                     "title": a.get("title"), "source": a.get("source")})
    return rows
