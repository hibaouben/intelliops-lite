import unittest
from src.contrat import Analyse, Evenement
from src.notification import choisir_canal, valider_action

def exemple(sensible=True, niveau="CRITICAL"):
    e = Evenement("EVT-00125", "2026-10-05T10:02:11Z", "DOCKER", "backend",
            "production", "LOG", "HIGH", "OOMKilled restarts=14")
    a = Analyse("EVT-00125", niveau, "Manque de memoire",
            "Redemarrer le service backend", sensible, ["DOCKER"])
    return e, a

class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "SLACK")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")
    def test_validation(self):
        _, a = exemple()
        self.assertTrue(valider_action(a, " OUI "))
        self.assertFalse(valider_action(a, "n"))    