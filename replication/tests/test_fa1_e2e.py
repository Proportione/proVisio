"""Tests del carril F-A1 end-to-end (Incremento 1) + invariantes del blueprint."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from provisio.ciclo_vida.aggregator import build_board
from provisio.l2_normalizacion import tri_estado, vectores
from provisio.l3_fusion import fusiones
from provisio.gobernanza import citacion, confirmacion
from evaluacion import componente_a_capacidad as compA


class TestTriEstado(unittest.TestCase):
    def test_na_no_es_cero(self):
        na = tri_estado.na_estructural("googleAdsCustomerId=null")
        self.assertIsNone(na["valor"])          # N/A != 0
        self.assertTrue(tri_estado.es_na(na))
        self.assertFalse(tri_estado.es_computable(na))

    def test_traza_vs_valor(self):
        self.assertEqual(tri_estado.traza(4, 10)["estado"], tri_estado.TRAZA)
        self.assertEqual(tri_estado.traza(200, 10)["estado"], tri_estado.VALOR)


class TestVectores(unittest.TestCase):
    def test_proporciones_suman_uno(self):
        v = vectores.vector_proporciones({"Direct": 210, "Organic": 74, "Referral": 16})
        self.assertAlmostEqual(sum(v.values()), 1.0)
        self.assertGreater(v["Direct"], v["Organic"])

    def test_na_no_divide_el_vector(self):
        # una celda N/A estructural no debe entrar en la normalización
        counts = {"Direct": 210, "Paid": tri_estado.na_estructural("sin ads")}
        v = vectores.vector_proporciones(counts)
        self.assertEqual(set(v.keys()), {"Direct"})
        self.assertAlmostEqual(v["Direct"], 1.0)

    def test_razon_acotada(self):
        self.assertEqual(vectores.razon_acotada(5, 25), 0.2)
        self.assertIsNone(vectores.razon_acotada(1, 0))


class TestFusionFA1(unittest.TestCase):
    def setUp(self):
        self.board = build_board({"mode": "snapshot"})

    def test_fusion_ejercida(self):
        fa1 = self.board["fusion"]["fa1"]
        self.assertEqual(fa1["estado_carril"], "ejercido")
        self.assertEqual(fa1["kpi"], "K1")
        self.assertEqual(fa1["entrada"], ["S1", "S2"])

    def test_fa4_no_ejercida(self):
        self.assertEqual(self.board["fusion"]["fa4"]["estado_carril"], "no_ejercido")

    def test_s3_na_estructural(self):
        self.assertTrue(tri_estado.es_na(self.board["signals"]["s3"]))

    def test_k1_censo_real(self):
        k1 = self.board["screens"]["k1"]
        self.assertEqual(k1["deals"], 216)          # cifra real del snapshot
        self.assertEqual(k1["contactos"], 500)
        self.assertEqual(k1["follow_ups_vencidos"], 11)

    def test_fr11_las_cifras_no_las_pone_el_llm(self):
        # sin ollama, brazo_L es None y la fusión SIGUE con brazo R (cifras deterministas)
        fa1 = self.board["fusion"]["fa1"]
        self.assertIsNone(fa1["brazo_L"])
        self.assertTrue(fa1["brazo_R"]["afirmaciones"])

    def test_citacion_por_afirmacion(self):
        fa1 = self.board["fusion"]["fa1"]
        rep = citacion.audita_fusion(fa1)
        self.assertGreaterEqual(rep["m1_brazo_R"], 0.90)  # cada afirmación cita su hecho

    def test_polaridad_por_tenant(self):
        adv = fusiones.fa1({"branded": {}}, {"channels": {}, "sessions": 0},
                           {"census": {}}, tenant="advertiser")
        self.assertEqual(adv["polaridad"], "retorno-inversion")


class TestGobernanzaSensible(unittest.TestCase):
    def test_bloqueo_eur_crudo(self):
        self.assertTrue(confirmacion.bloqueo_sensible("cerramos 40.000 € este mes"))
        self.assertFalse(confirmacion.bloqueo_sensible("pipeline sano"))


class TestComponenteA(unittest.TestCase):
    def test_capacidad_verde_y_fiel(self):
        # audit_log_path a temp: el test NO contamina la bitácora de evidencia commiteada
        with tempfile.TemporaryDirectory() as d:
            res = compA.run("fa1", {"mode": "snapshot",
                                    "audit_log_path": os.path.join(d, "audit.jsonl")})
        self.assertTrue(res["checklist_verde"], res["checklist"])
        self.assertTrue(res["fidelidad_censo_ok"], res["fidelidad_detalle"])
        self.assertTrue(res["reproducible"])

    def test_componente_a_deja_audit_trail(self):
        # la corrida de Componente A debe emitir evidencia de bitácora (R2)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "audit.jsonl")
            compA.run("fa1", {"mode": "snapshot", "audit_log_path": p})
            self.assertTrue(os.path.exists(p), "Componente A no dejó audit-trail")
            rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
            claims = [r for r in rows if r.get("event") == "fusion_claim"]
            self.assertTrue(claims, "sin filas fusion_claim en la bitácora")
            self.assertEqual(claims[0]["fusion"], "F-A1")
            self.assertTrue(all(c.get("citas") for c in claims))  # cada afirmación cita
            # una sola pasada auditada (b1); b2 no duplica el corpus
            self.assertEqual(len({(c["brazo"], c["texto"]) for c in claims}), len(claims))


class TestAuditTrailBuildBoard(unittest.TestCase):
    def test_audit_off_por_defecto_no_escribe(self):
        # build_board es función pura por defecto: no toca la bitácora
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "audit.jsonl")
            build_board({"mode": "snapshot", "audit_log_path": p})
            self.assertFalse(os.path.exists(p))

    def test_audit_on_emite_log_fusion(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "audit.jsonl")
            build_board({"mode": "snapshot", "audit_log_path": p}, audit=True)
            self.assertTrue(os.path.exists(p))
            rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
            self.assertTrue(any(r.get("event") == "fusion_claim" for r in rows))


if __name__ == "__main__":
    unittest.main()
