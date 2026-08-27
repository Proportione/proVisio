"""L4 — Vistas KPI por tenant (K1-K5).

Ensambla la vista de negocio que consume L5, a partir del colector operativo
(op_crm para K1) y de la lectura de fusión de L3. Deriva del esquema de pantallas
de `aggregator._empty_screens` del wallboard, reorganizado por familia K.

Incremento 1: k1_acquisition. K2-K5 se pueblan en Incr. 2-3 (ver vistas.py).
"""
