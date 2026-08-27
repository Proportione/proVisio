"""Ciclo de vida — orquestador transversal.

  aggregator.py  poll_once/run, is_stale (3xCADENCE), último-bueno, compose del board.
  alertas.py     derive_alerts (brazo R en vivo, ISA-18.2) + alert_transitions.
  cache.py       último board bueno (thread-safe + persistencia best-effort).

Portado verbatim en su semántica del wallboard (frescura, degradación, alertas); la
única reorganización es que compone el board del artefacto (signals/screens/fusion).
"""
