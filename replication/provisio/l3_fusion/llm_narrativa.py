"""Brazo L — narrativa mediada por LLM. Capa NARRATIVA, no autoritativa.

VENDORIZADO de wallboard/sources/insight.py (qwen3:14b local, Ollama, €0), reencuadrado
a la fusión F-A1. REGLA DURA FR-11: los hechos NO pasan por el LLM. El brazo L recibe
los hechos YA calculados por el brazo R (reglas.py) y solo los REDACTA en lenguaje
natural; no produce ninguna cifra que vaya a una tarjeta. Aditivo y opcional: si el
qwen no responde o alucina, `narrar_fa1` lanza -> la fusión degrada al brazo R y el
frontend oculta la IA (la TV sigue).

El control 20-60-20 (gobernanza/) envuelve este brazo: cada frase generada debe
poder anclarse a un hecho (citación-por-afirmación), o la gobernanza la bloquea.
"""

import json
import os
import urllib.request

OLLAMA_URL_DEFAULT = os.environ.get("PROVISIO_OLLAMA_URL", "http://localhost:11434")
MODEL_DEFAULT = "qwen3:14b"

_SYSTEM = (
    "Eres el copiloto de una plataforma de inteligencia de negocio (nodo Aveiro, "
    "Proportione). Hablas español, sobrio, sala de control. REGLA ABSOLUTA: solo "
    "puedes reformular los hechos que te doy; NO inventes cifras, nombres ni hechos "
    "fuera del contexto. No saludes, no uses emojis."
)


def _prompt(hechos_r):
    lineas = "\n".join("- " + a["texto"] for a in hechos_r.get("afirmaciones", []))
    return (
        _SYSTEM + "\n\nFUSIÓN F-A1 (interés de búsqueda + analítica web -> adquisición). "
        "HECHOS ya calculados de forma determinista:\n" + lineas +
        "\n\nDevuelve SOLO un objeto JSON: "
        '{"sintesis": "1-2 frases que priorizan qué mirar, SIN cifras nuevas"}\n'
        "Español. Sin inventar datos."
    )


def call_qwen(ollama_url, model, prompt, timeout=30):
    """Llama al Ollama local (/api/generate). Lanza si no se puede -> degradación.
    VERBATIM de insight.py: think:false, sin format:json (colapsa qwen3)."""
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.3, "num_predict": 300},
    }).encode("utf-8")
    req = urllib.request.Request(
        ollama_url.rstrip("/") + "/api/generate",
        data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8")).get("response", "")


def parse(raw, model, hechos_r):
    """Valida la salida del LLM. Cada frase HEREDA las citas de las afirmaciones R
    que reformula (no puede citar lo que R no dijo). Lanza si no hay nada usable."""
    if not raw or "{" not in raw:
        raise ValueError("respuesta IA vacía/sin JSON")
    frag = raw[raw.index("{"):raw.rindex("}") + 1]
    data = json.loads(frag)
    sintesis = " ".join(str(data.get("sintesis") or "").split())[:280]
    if not sintesis:
        raise ValueError("respuesta IA sin contenido usable")
    # citas del brazo L = unión de las citas del brazo R (redacta SOBRE ellas, FR-11)
    citas = sorted({c for a in hechos_r.get("afirmaciones", []) for c in a.get("citas", [])})
    return {"brazo": "L", "modelo": model, "sintesis": sintesis, "citas": citas}


def narrar_fa1(s1, s2, k1, hechos_r, config=None):
    """Callable para fusiones.fa1(brazo_l=...). Redacta la síntesis F-A1 con el qwen
    local. Lanza si el LLM no está disponible/alucina (la fusión degrada al brazo R)."""
    config = config or {}
    url = config.get("ollama_url", OLLAMA_URL_DEFAULT)
    model = config.get("insight_model", MODEL_DEFAULT)
    raw = call_qwen(url, model, _prompt(hechos_r),
                    timeout=int(config.get("insight_timeout", 30) or 30))
    return parse(raw, model, hechos_r)
