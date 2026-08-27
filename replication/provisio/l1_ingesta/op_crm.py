"""op_crm — Colector CRM. Alimenta K1 Acquisition (y K2 Revenue, con gate de
anonimización, en Incremento 3).

VENDORIZADO de nodo-aveiro/tools/wallboard/wallboard/sources/leads.py: `build_leads`
y sus 7 helpers se copian con CUERPO Y COMENTARIOS VERBATIM (reusa la lógica del
colector REAL de producción; no se reimplementa ni se inventan datos). Lo único
adaptado es el envoltorio de contexto: los docstrings de módulo/función (naming por
capas: "screens['leads']" → sub-árbol CRM = K1) y `collect()`, que en modo --snapshot
lee el snapshot congelado en vez de llamar a core-api con la doble-auth.

Contrato de datos (verificado contra core-api/crm/repository.mjs):
  - valorTotal es STRING SIEMPRE -> parseFloat estilo JS (prefijo numérico).
  - 'Ganado'/'Ganada' y 'Perdido'/'Perdida' son formas cerradas válidas.
  - Deals con label 'test' o nombre [TEST] fuera de métrica (CLAUDE.md regla 5).
"""

import re
import unicodedata
from datetime import datetime, timezone

from .. import clients
from ._snapshot import load

NAME = "op_crm"
CADENCE_SECONDS = 600
FAMILIA = ("K1", "K2")  # Acquisition + Revenue (K2 con gate de anonimización, Incr. 3)

# --- helpers VERBATIM de leads.py ---------------------------------------------

STAGE_PROBABILITY = {
    "leads": 0.10, "contactados": 0.25, "propuesta hecha": 0.50, "propuesta": 0.50,
    "presentacion": 0.60, "negociacion": 0.75, "ganado": 1.0, "ganada": 1.0,
    "perdido": 0.0, "perdida": 0.0,
}

COLUMNAS = (
    ("leads", "Leads"),
    ("cont", "Contactados"),
    ("prop", "Propuesta"),
    ("nego", "Negociación"),
    ("win", "Ganado"),
)
ACTIVAS = ("leads", "cont", "prop", "nego")

_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _norm(s):
    """minúsculas sin acentos para comparar etapas robustamente."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return s.lower().strip()


def _col(etapa):
    """Mapea una etapa libre a la columna del kanban, o None (Perdido/Sin etapa/desconocida)."""
    n = _norm(etapa)
    if n == "leads":
        return "leads"
    if n.startswith("contact"):
        return "cont"
    if n.startswith("propuesta"):
        return "prop"
    if n.startswith("negocia") or n.startswith("presentac"):
        return "nego"
    if n in ("ganado", "ganada"):
        return "win"
    return None  # perdido / sin etapa / no canónica -> fuera del kanban


def _money(n):
    """Abrevia euros para glance (1,0 M € / 84 K € / 40 €). Coma decimal ES."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "—"
    if abs(n) >= 1_000_000:
        return (f"{n / 1_000_000:.1f}".replace(".", ",")) + " M €"
    if abs(n) >= 1000:
        return f"{int(round(n / 1000))} K €"
    return f"{int(round(n))} €"


def _valor(d):
    """valorTotal viene STRING; parsea estilo JS parseFloat (mismo criterio que el
    backend usa para pipelineValor). Prefijo numérico; '' o no-numérico -> 0.0."""
    raw = d.get("valorTotal")
    if raw is None:
        raw = d.get("totalValue")
    m = _NUM.match(str(raw or "").strip())
    return float(m.group()) if m else 0.0


def _etapa(d):
    return (d.get("etapa") or d.get("stage") or "Sin etapa").strip()


def _is_test(d):
    nombre = (d.get("nombre") or "").upper()
    labels = {str(x).lower() for x in (d.get("labels") or [])}
    return nombre.startswith("[TEST]") or "test" in labels or d.get("source") == "test"


def _plazo(d, today):
    """(texto, estado, dias_vencido) del seguimiento (nextFollowUp) frente a `today`.
    '' / 'Invalid date' / fecha no parseable -> sin seguimiento. La ventana temporal
    explícita ('+N d') evita leer un cálculo vivo como KPI estable (mismatch señal↔KPI)."""
    raw = str(d.get("nextFollowUp") or d.get("next_follow_up") or "").split("T")[0].strip()
    if not raw or raw.lower() == "invalid date":
        return None, "ok", 0
    try:
        delta = (datetime.strptime(today, "%Y-%m-%d").date()
                 - datetime.strptime(raw, "%Y-%m-%d").date()).days
    except ValueError:
        return None, "ok", 0
    if delta > 0:
        return f"vencido +{delta} d", "crit", delta
    if delta == 0:
        return "seguir hoy", "warn", 0
    return f"seguir {raw}", "wait", 0


def _follow_delta(d, today):
    """Días con signo entre HOY y nextFollowUp (>0 vencido, 0 hoy, <0 futuro). None si no hay fecha."""
    raw = str(d.get("nextFollowUp") or d.get("next_follow_up") or "").split("T")[0].strip()
    if not raw or raw.lower() == "invalid date":
        return None
    try:
        return (datetime.strptime(today, "%Y-%m-%d").date()
                - datetime.strptime(raw, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def _fecha_cierre_dias(d, today):
    """Días hasta fechaCierre (futuro). None si no hay fecha, no parsea o ya pasó."""
    raw = str(d.get("fechaCierre") or "").split("T")[0].strip()
    if not raw or raw.lower() == "invalid date":
        return None
    try:
        dias = (datetime.strptime(raw, "%Y-%m-%d").date()
                - datetime.strptime(today, "%Y-%m-%d").date()).days
    except ValueError:
        return None
    return dias if dias >= 0 else None


def _slug(d):
    return (clients.resolve(d.get("company"))
            or clients.resolve(d.get("contactoPrincipal"))
            or clients.resolve(d.get("nombre")))


def build_leads(deals_raw, stats_raw, today):
    """Compone el sub-árbol CRM (screens['leads'] en producción) a partir de /deals +
    /stats. Pura/testeable. NO reclasifica etapas ni recalcula prioridad: toma los
    campos de core-api. Cuerpo y comentarios VERBATIM de wallboard/sources/leads.py;
    el docstring se adapta al naming por capas del artefacto (sub-árbol CRM = K1)."""
    deals = [d for d in (deals_raw.get("deals") or []) if not _is_test(d)]
    mes = today[:7]  # YYYY-MM

    buckets = {k: [] for k, _ in COLUMNAS}
    valor_col = {k: 0.0 for k, _ in COLUMNAS}
    ponderado = 0.0
    ganados_valor = 0.0

    for d in deals:
        col = _col(_etapa(d))
        if col is None:
            continue
        v = _valor(d)
        if col == "win":
            cierre = str(d.get("fechaCierre") or d.get("updatedAt") or "")[:7]
            if cierre != mes:
                continue  # la columna Ganado muestra SOLO el mes en curso
            buckets["win"].append(d)
            valor_col["win"] += v
            ganados_valor += v
            continue
        buckets[col].append(d)
        valor_col[col] += v
        ponderado += v * STAGE_PROBABILITY.get(_norm(_etapa(d)), 0.0)

    # seguimientos limpios (recalculados desde /deals, NO desde stats.followUps)
    venc = hoy = prox = 0
    vencidos = []  # (dias_vencido, valor, deal)
    acciones = []  # (orden, item)  -> próximas acciones nombradas, ordenadas por fecha
    for col in ACTIVAS:
        for d in buckets[col]:
            plazo, pstate, dias = _plazo(d, today)
            if pstate == "crit":
                venc += 1
                vencidos.append((dias, _valor(d), d))
            elif pstate == "warn":
                hoy += 1
            elif pstate == "wait":
                prox += 1
            delta = _follow_delta(d, today)
            if delta is not None:  # tiene seguimiento -> es una acción ordenable por fecha
                v = _valor(d)
                acciones.append((-delta, {
                    "titulo": (d.get("nombre") or "(sin nombre)")[:60],
                    "cliente_slug": _slug(d), "company": (d.get("company") or "")[:40],
                    "valor": _money(v) if v else "", "plazo": plazo or "",
                    "plazo_state": pstate, "state": pstate,
                }))
    # vencidos primero (más vencido arriba), luego hoy, luego próximos por fecha asc. Cap 6.
    proximas_acciones = [it for _, it in sorted(acciones, key=lambda x: x[0])][:6]

    # el seguimiento que más urge (más vencido; el valor desempata) sube a héroe:
    # nombra el QUÉ accionable ('a quién llamo HOY antes de que se enfríe').
    seguir_top = None
    if vencidos:
        dias, val, d = max(vencidos, key=lambda x: (x[0], x[1]))
        seguir_top = {"titulo": (d.get("nombre") or "")[:48], "cliente_slug": _slug(d),
                      "dias": dias, "valor": _money(val) if val else ""}

    # próximos cierres: deals activos ordenados por cercanía a la venta (fechaCierre asc;
    # sin fecha -> por probabilidad de etapa y valor). Nombrados, con €. Cap 6.
    activos = [d for col in ACTIVAS for d in buckets[col]]

    def _cierre_key(d):
        dias = _fecha_cierre_dias(d, today)
        if dias is None:
            return (1, -STAGE_PROBABILITY.get(_norm(_etapa(d)), 0.0), -_valor(d))
        return (0, dias, -_valor(d))

    proximos_cierres = []
    for d in sorted(activos, key=_cierre_key)[:6]:
        dias = _fecha_cierre_dias(d, today)
        proximos_cierres.append({
            "titulo": (d.get("nombre") or "(sin nombre)")[:60], "cliente_slug": _slug(d),
            "company": (d.get("company") or "")[:40],
            "valor": _money(_valor(d)) if _valor(d) else "—",
            "etapa": _etapa(d), "prob": int(round(STAGE_PROBABILITY.get(_norm(_etapa(d)), 0.0) * 100)),
            "cierre_txt": (f"{dias} d" if dias is not None else _etapa(d)), "dias": dias,
        })

    # ganados/perdidos del MES (eventos recientes) + alerta de ganado (positiva).
    perdidos_mes = [d for d in deals if _norm(_etapa(d)) in ("perdido", "perdida")
                    and str(d.get("fechaCierre") or d.get("updatedAt") or "")[:7] == mes]

    def _fc(d):
        return str(d.get("fechaCierre") or d.get("updatedAt") or "")

    eventos = [("Ganado", d) for d in buckets["win"]] + [("Perdido", d) for d in perdidos_mes]
    eventos.sort(key=lambda ed: _fc(ed[1]), reverse=True)
    ganados_recientes = [{
        "titulo": (d.get("nombre") or "(sin nombre)")[:60], "cliente_slug": _slug(d),
        "company": (d.get("company") or "")[:40], "valor": _money(_valor(d)) if _valor(d) else "",
        "fecha": _fc(d)[:10], "evt": evt, "state": "ok" if evt == "Ganado" else "wait",
    } for evt, d in eventos[:5]]

    alerta_ganado = None
    if buckets["win"]:
        w = sorted(buckets["win"], key=_fc, reverse=True)[0]
        alerta_ganado = {"titulo": (w.get("nombre") or "")[:48], "cliente_slug": _slug(w),
                         "valor": _money(_valor(w)) if _valor(w) else ""}

    # ganados del mes nombrados (alimenta la pantalla Éxitos).
    ganados_lista = [{
        "titulo": (d.get("nombre") or "(sin nombre)")[:80], "cliente_slug": _slug(d),
        "valor": _money(_valor(d)) if _valor(d) else "", "company": (d.get("company") or "")[:40],
    } for d in sorted(buckets["win"], key=lambda d: -_valor(d))]

    propuestas = len(buckets["prop"]) + len(buckets["nego"])
    ganados_mes = len(buckets["win"])

    # KPIs de pipeline: prefiere los ya agregados por core-api (parseFloat consistente)
    s_deals = (stats_raw or {}).get("deals") or {}
    valor_pipeline = s_deals.get("pipelineValor")
    if not isinstance(valor_pipeline, (int, float)):
        valor_pipeline = sum(valor_col[k] for k in ACTIVAS)
    activas_total = s_deals.get("activeCount")
    if not isinstance(activas_total, int):
        activas_total = sum(len(buckets[k]) for k in ACTIVAS)

    # copy accionable (FR-10): nombra el próximo movimiento concreto (deal + cliente +
    # ventana), no una etiqueta genérica.
    if seguir_top:
        nombre = seguir_top["titulo"][:34]
        accion = f"Llamar a {nombre} (vencido +{seguir_top['dias']} d)"
        if venc > 1:
            accion += f" · y {venc - 1} más"
    elif hoy:
        accion = f"{hoy} seguimiento(s) a hacer hoy"
    elif ganados_mes:
        accion = f"Buen mes: {ganados_mes} cerrado(s) · a por el siguiente"
    else:
        accion = "Pipeline al día — sin seguimientos pendientes"

    return {
        "valor_pipeline": _money(valor_pipeline),
        "activas": int(activas_total or 0),
        "ponderado": _money(ponderado),
        "seguir_vencidos": venc, "seguir_hoy": hoy, "seguir_proximos": prox,
        "seguir_top": seguir_top,
        "ganados_mes": ganados_mes, "ganados_valor": _money(ganados_valor) if ganados_valor else "",
        "propuestas": propuestas,
        "accion": accion,
        "proximas_acciones": proximas_acciones,
        "proximos_cierres": proximos_cierres,
        "ganados_recientes": ganados_recientes,
        "alerta_ganado": alerta_ganado,
        "ganados_lista": ganados_lista,
    }


# --- collect: única pieza NUEVA (snapshot-aware) ------------------------------

def collect(config):
    """Sub-árbol CRM. En modo --snapshot lee `crm.json` (censo real + shape-fixture
    de deals) y ejerce `build_leads` verbatim sobre ella. Adjunta `census` (cifras
    reales congeladas) como cabecera autoritativa de K1."""
    if (config or {}).get("mode", "snapshot") != "snapshot":
        raise NotImplementedError(
            "op_crm modo --live diferido: core_get(/api/crm/deals) con doble-auth SA "
            "(id_token + x-internal-auth), idéntico a wallboard/sources/leads.py. "
            "Incremento 1 usa el snapshot congelado.")
    snap = load("crm.json", config)
    today = snap.get("today") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = build_leads({"deals": snap.get("deals", [])}, snap.get("stats", {}), today)
    out["census"] = snap.get("census", {})  # cifras reales (216 deals, 500 contactos, ...)
    return out
