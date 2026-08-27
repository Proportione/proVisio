"""K1 Acquisition — vista de negocio.

Cabecera autoritativa = `census` (cifras reales congeladas: 500 contactos, 216 deals,
11 follow-ups vencidos). El desglose de pipeline/seguimientos lo aporta `build_leads`
(op_crm) ejercido sobre la shape-fixture. La lectura de fusión (F-A1) se adjunta como
capa interpretativa, con su brazo R (autoritativo) y su brazo L (narrativa, si hay).
"""


def build_k1(op_crm_out, fa1):
    """Ensambla screens['k1']. Pura/testeable."""
    census = (op_crm_out or {}).get("census") or {}
    return {
        "familia": "K1",
        "titulo": "Adquisición",
        "fuerza_senal": "alta",  # etiquetado de heterogeneidad (blueprint §4)
        # --- cabecera real (census congelado) ---
        "contactos": census.get("contactos"),
        "clientes": census.get("clientes"),
        "leads": census.get("leads"),
        "prospectos": census.get("prospectos"),
        "deals": census.get("deals"),
        "follow_ups_vencidos": census.get("follow_ups_vencidos"),
        # --- desglose de pipeline (build_leads sobre shape-fixture) ---
        "pipeline": {
            "valor_pipeline": op_crm_out.get("valor_pipeline"),
            "activas": op_crm_out.get("activas"),
            "ponderado": op_crm_out.get("ponderado"),
            "propuestas": op_crm_out.get("propuestas"),
            "ganados_mes": op_crm_out.get("ganados_mes"),
            "proximas_acciones": op_crm_out.get("proximas_acciones", []),
            "proximos_cierres": op_crm_out.get("proximos_cierres", []),
        },
        "accion": op_crm_out.get("accion"),
        # --- lectura de fusión F-A1 (L3) ---
        "fusion_lectura": (fa1 or {}).get("brazo_R", {}).get("lectura"),
        "fusion_narrativa": ((fa1 or {}).get("brazo_L") or {}).get("sintesis"),
    }
