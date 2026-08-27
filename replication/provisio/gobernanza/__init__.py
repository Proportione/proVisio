"""Gobernanza — superficie evaluable del control 20-60-20 (C-4, P2).

`20-60-20` es la ETIQUETA del patrón de control (encuadre humano / redacción LLM /
verificación-auditoría humana), NO un ratio de esfuerzo medido (gap G6). Este paquete
instrumenta y expone los TRES controles, evaluables por M1-M5:

  confirmacion.py  control 1 — gate: una afirmación LLM no alcanza superficie de
                   decisión sin respaldo determinista.
  citacion.py      control 2 — citación-por-afirmación: cada frase LLM ancla a un hecho.
  audit_trail.py   control 3 — bitácora append-only (ENCENDIDA en el artefacto).

El módulo/paper NO afirma el reparto 20/60/20 de esfuerzo.
"""
