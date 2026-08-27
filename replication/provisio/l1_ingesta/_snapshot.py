"""Cargador del snapshot congelado (gate G1).

En modo `--snapshot` los colectores L1 leen del snapshot datado en
`evaluacion/snapshot/` en vez de tocar red. Esto hace el pipeline reproducible
por un tercero, offline y €0 (determinismo salvo la etapa LLM opcional de L3).

En modo `--live` (diferido) los colectores acuñarían un id_token de la SA y
llamarían a core-api / BI MCP con la doble-auth existente — misma credencial que
el wallboard de producción, sin añadir secretos.
"""

import json
from pathlib import Path

# provisio/l1_ingesta/_snapshot.py -> .../provisio-artifact/evaluacion/snapshot/
SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "evaluacion" / "snapshot"


def load(nombre, config=None):
    """Lee `evaluacion/snapshot/<nombre>`. `config['snapshot_dir']` lo sobreescribe
    (para tests). Lanza si no existe -> el aggregator marca el bloque stale."""
    base = Path((config or {}).get("snapshot_dir") or SNAPSHOT_DIR)
    with open(base / nombre, encoding="utf-8") as f:
        return json.load(f)
