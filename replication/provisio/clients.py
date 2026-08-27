"""Resolución cliente -> slug (FR-09). VENDORIZADO de
nodo-aveiro/tools/wallboard/wallboard/clients.py (copiado, no importado: el
artefacto no comparte historia con IT Proportione). Para el paquete público el
roster real de tenants se sustituye por slugs genéricos (tenant-a..d): los
nombres de clientes son información comercial confidencial. La LÓGICA de
resolución (alias -> slug canónico, fallback a chip-monograma) es la real.

La UI pinta assets/clients/<slug>.(svg|png); si el asset no existe -> fallback a
chip-monograma con color de marca. Aquí solo se resuelve el slug canónico a partir
de señales (tag de ticket, remitente de email, nombre de repo).
"""

# Slugs canónicos (FR-09). Genéricos en el paquete público.
SLUGS = ("tenant-a", "tenant-b", "tenant-c", "tenant-d", "proportione")

# Alias -> slug. Cubre tags, dominios de remitente y nombres de repo.
ALIASES = {
    "tenant-a": "tenant-a",
    "ta": "tenant-a",
    "tenant-b": "tenant-b",
    "tb": "tenant-b",
    "tenant-c": "tenant-c",
    "tc": "tenant-c",
    "tenant-d": "tenant-d",
    "td": "tenant-d",
    "proportione": "proportione",
    "prop": "proportione",
}

# slug -> clase de chip del CSS (monograma de marca como fallback).
CHIP_CLASS = {
    "tenant-a": "c-ta",
    "tenant-b": "c-tb",
    "tenant-c": "c-tc",
    "tenant-d": "c-td",
    "proportione": "c-prop",
}


def resolve(signal):
    """Devuelve el slug canónico para `signal` (tag, remitente o repo), o None."""
    if not signal:
        return None
    s = str(signal).lower()
    if s in ALIASES:
        return ALIASES[s]
    for alias, slug in ALIASES.items():
        if alias in s:
            return slug
    return None


def chip_class(slug):
    """Clase CSS del chip-monograma de fallback para `slug`."""
    return CHIP_CLASS.get(slug, "c-prop")
