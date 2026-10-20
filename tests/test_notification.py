import unittest
from src.contrat import Analyse, Evenement
from src.notification import (choisir_canal, notifier, rediger, tracer_decision, valider_action)

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
    
    def test_rediger(self):
        e, a = exemple()
        texte = rediger(e, a)
        lignes = texte.split("\n")
        self.assertEqual(len(lignes), 5)
        self.assertEqual(lignes[0], "[CRITICAL] Composant : backend")
        self.assertEqual(lignes[1], "Evenement : OOMKilled restarts=14")
        self.assertEqual(lignes[2], "Explication : Manque de memoire")
        self.assertEqual(lignes[3], "Action proposee : Redemarrer le service backend")
        self.assertEqual(lignes[4], "Sources : DOCKER")

    def test_notifier(self):
        e, a = exemple()
        historique = []
        notif = notifier(e, a, historique)
        self.assertEqual(notif.event_id, "EVT-00125")
        self.assertEqual(notif.channel, "TEAMS")
        self.assertEqual(notif.recipient, "equipe-ops")
        self.assertEqual(notif.text, rediger(e, a))
        self.assertEqual(historique, [notif])
        self.assertEqual(e.status, "NOTIFIED")

        
    def test_validation_refus(self):
        _, a = exemple()
        self.assertFalse(valider_action(a, ""))
        self.assertFalse(valider_action(a, "non"))
        self.assertTrue(valider_action(a, "Yes"))
        self.assertTrue(valider_action(a, " ok "))

    def test_validation_action_non_sensible(self):
        _, a = exemple(sensible=False, niveau="LOW")
        self.assertTrue(valider_action(a, "n"))

    def test_tracer_decision(self):
        _, a = exemple()
        journal = []
        entree = tracer_decision(a, True, "ops-oncall", journal,
                                 "2026-10-05T10:10:00Z")
        self.assertEqual(entree, {
            "event_id": "EVT-00125",
            "action": "Redemarrer le service backend",
            "approved": True,
            "actor": "ops-oncall",
            "timestamp": "2026-10-05T10:10:00Z",
        })
        self.assertEqual(journal, [entree])  