"""Brazo R — baseline determinista de la fusión (Componente C).

Reglas explícitas, umbrales y mapeos señal->KPI tabulados. 0 alucinación por
construcción. Deriva del estilo de `sources/success.py` del wallboard (derivación
determinista de indicadores desde el snapshot de pantallas). Produce, para cada
fusión, la LECTURA determinista y las CITAS (afirmación -> hecho fuente) que el
brazo L deberá igualar o superar sin contradecir.
"""


def lectura_fa1(s1, s2, k1):
    """Lectura determinista de F-A1 (S1+S2 -> K1). Devuelve frases + citas.

    Cada frase porta su(s) `cita(s)`: id de fuente en el snapshot (control 2,
    citación-por-afirmación). Ninguna cifra se inventa: todas salen de s1/s2/k1."""
    census = (k1 or {}).get("census") or {}
    br = (s1 or {}).get("branded") or {}
    mix = (s2 or {}).get("channel_mix") or {}
    directo = mix.get("Direct")
    organico = mix.get("Organic")

    afirmaciones = []

    afirmaciones.append({
        "texto": (f"Demanda observada: {s1.get('queries_total', 0)} consultas de búsqueda y "
                  f"{s2.get('sessions', 0)} sesiones web en la ventana."),
        "citas": ["s1.queries_total", "s2.sessions"],
    })
    if directo is not None:
        afirmaciones.append({
            "texto": (f"El tráfico está dominado por acceso Directo "
                      f"({directo * 100:.0f}%), con Orgánico al "
                      f"{(organico or 0) * 100:.0f}%: adquisición por marca/relación, no por SEO."),
            "citas": ["s2.channel_mix.Direct", "s2.channel_mix.Organic"],
        })
    afirmaciones.append({
        "texto": (f"Señal de marca floja: '{br.get('query')}' con {br.get('impressions')} "
                  f"impresiones y CTR {(br.get('ctr') or 0):.2%}."),
        "citas": ["s1.branded.impressions", "s1.branded.ctr"],
    })
    afirmaciones.append({
        "texto": (f"El funnel real (K1) sostiene {census.get('deals', 0)} deals sobre "
                  f"{census.get('contactos', 0)} contactos, con "
                  f"{census.get('follow_ups_vencidos', 0)} follow-ups vencidos."),
        "citas": ["k1.census.deals", "k1.census.contactos", "k1.census.follow_ups_vencidos"],
    })

    return {
        "brazo": "R",
        "kpi": "K1",
        "afirmaciones": afirmaciones,
        "lectura": ("Demanda entrante fina y de marca floja; la adquisición se apoya en "
                    "acceso Directo y en un funnel CRM ya poblado. Prioridad: higiene de "
                    f"follow-ups ({census.get('follow_ups_vencidos', 0)} vencidos)."),
    }
