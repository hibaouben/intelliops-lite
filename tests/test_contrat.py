import unittest

from src.contrat import NIVEAUX, PROCEDURES, Evenement


class TestContrat(unittest.TestCase):
    def test_statut_par_defaut(self):
        e = Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", "backend",
                      "production", "LOG", "LOW", "demarrage")
        self.assertEqual(e.status, "NEW")

    def test_niveaux_ordonnes(self):
        self.assertEqual(NIVEAUX[0], "LOW")
        self.assertEqual(NIVEAUX[-1], "CRITICAL")

    def test_base_procedures(self):
        self.assertIn("oomkilled", PROCEDURES)
