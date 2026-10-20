import unittest
from src.analyse import (
    analyser,
    classifier,
    compter_erreurs,
    est_doublon,
    chercher_procedures,
)
from src.contrat import PROCEDURES, Evenement


def evt(type_="LOG", severity="HIGH", message="OOMKilled restarts=14", composant="backend", source="DOCKER"):
    return Evenement("EVT-00001", "2026-10-05T10:00:00Z", source, composant, "production", type_, severity, message)


class TestAnalyse(unittest.TestCase):

    def test_doublon(self):
        vus = set()
        e = evt()
        self.assertFalse(est_doublon(e, vus))
        self.assertTrue(est_doublon(e, vus))

    def test_compter_erreurs(self):
        compteur = {}
        e_log_high = evt(type_="LOG", severity="HIGH")
        self.assertEqual(compter_erreurs(e_log_high, compteur), 1)

    def test_chercher_procedures(self):
        e = evt(message="Erreur oomkilled sur le serveur")
        procs = chercher_procedures(e, PROCEDURES)
        self.assertIn(PROCEDURES["oomkilled"], procs)

    def test_classifier(self):
        e = evt()
        self.assertEqual(classifier(e, 3), "CRITICAL")

    def test_analyser(self):
        e = evt(type_="VULNERABILITY", severity="HIGH", composant="lib-xyz")
        a = analyser(e, PROCEDURES)
        self.assertEqual(a.action, "Mettre a jour la dependance lib-xyz")


if __name__ == "__main__":
    unittest.main()
