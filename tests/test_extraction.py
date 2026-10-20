import unittest

from src.extraction import (masquer_secrets, normaliser_log,
                            normaliser_pipeline, normaliser_scan)

LIGNE = "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123"
SCAN = {"cve": "CVE-2026-1234", "package": "lib-xyz", "severity": "critical",
        "date": "2026-10-05T10:07:00Z"}
PIPELINE = {"job": "build", "status": "failed", "date": "2026-10-05T10:06:00Z"}


class TestMasquerSecrets(unittest.TestCase):
    def test_masquer_secrets(self):
        self.assertEqual(masquer_secrets("user=bob password=abc123"),
                         "user=bob password=[SECRET]")

    def test_tous_les_noms_de_parametres(self):
        for nom in ("password", "passwd", "token", "secret", "api_key", "apikey"):
            with self.subTest(nom=nom):
                self.assertEqual(masquer_secrets(f"{nom}=xyz"), f"{nom}=[SECRET]")

    def test_casse_ignoree(self):
        self.assertEqual(masquer_secrets("PassWord=abc"), "PassWord=[SECRET]")

    def test_forme_deux_points(self):
        self.assertEqual(masquer_secrets("token: abc123 ok"),
                         "token: [SECRET] ok")

    def test_separateurs_de_fin(self):
        self.assertEqual(masquer_secrets("token=a1&user=bob"),
                         "token=[SECRET]&user=bob")
        self.assertEqual(masquer_secrets("secret=a1,x secret=b2;y"),
                         "secret=[SECRET],x secret=[SECRET];y")

    def test_texte_sans_secret_inchange(self):
        self.assertEqual(masquer_secrets("Service demarre"), "Service demarre")

    def test_bearer(self):
        self.assertEqual(masquer_secrets("Authorization: Bearer eyJ.abc-1"),
                         "Authorization: Bearer [SECRET]")


class TestNormaliserLog(unittest.TestCase):
    def test_normaliser_log(self):
        evt = normaliser_log(LIGNE, 42)
        self.assertEqual(evt.id, "EVT-00042")
        self.assertEqual(evt.timestamp, "2026-10-05T10:02:11Z")
        self.assertEqual(evt.severity, "HIGH")
        self.assertNotIn("abc123", evt.message)

    def test_champs_du_contrat(self):
        evt = normaliser_log(LIGNE, 1)
        self.assertEqual(evt.source, "DOCKER")
        self.assertEqual(evt.environment, "production")
        self.assertEqual(evt.component, "backend")
        self.assertEqual(evt.event_type, "LOG")
        self.assertEqual(evt.message, "OOMKilled restarts=14 password=[SECRET]")
        self.assertEqual(evt.status, "NEW")

    def test_severites(self):
        attendu = {"CRITICAL": "CRITICAL", "fatal": "CRITICAL", "ERROR": "HIGH",
                   "warn": "MEDIUM", "WARNING": "MEDIUM", "INFO": "LOW",
                   "DEBUG": "LOW"}
        for niveau, severite in attendu.items():
            with self.subTest(niveau=niveau):
                ligne = f"2026-10-05 10:00:00 {niveau} api message"
                self.assertEqual(normaliser_log(ligne, 1).severity, severite)

    def test_ligne_trop_courte(self):
        with self.assertRaises(ValueError):
            normaliser_log("2026-10-05 10:00:00 ERROR backend", 1)


class TestNormaliserScan(unittest.TestCase):
    def test_normaliser_scan(self):
        evt = normaliser_scan(SCAN, 8)
        self.assertEqual(evt.id, "EVT-00008")
        self.assertEqual(evt.source, "TRIVY")
        self.assertEqual(evt.component, "lib-xyz")
        self.assertEqual(evt.event_type, "VULNERABILITY")
        self.assertEqual(evt.timestamp, "2026-10-05T10:07:00Z")
        self.assertEqual(evt.severity, "CRITICAL")
        self.assertEqual(evt.message, "Vulnerabilite CVE-2026-1234 dans lib-xyz")

    def test_severite_inconnue(self):
        self.assertEqual(normaliser_scan({**SCAN, "severity": "grave"}, 1).severity,
                         "LOW")

    def test_cle_manquante(self):
        rapport = dict(SCAN)
        del rapport["cve"]
        with self.assertRaises(ValueError):
            normaliser_scan(rapport, 1)


class TestNormaliserPipeline(unittest.TestCase):
    def test_pipeline_en_echec(self):
        evt = normaliser_pipeline({**PIPELINE, "status": "FAILED"}, 7)
        self.assertEqual(evt.id, "EVT-00007")
        self.assertEqual(evt.source, "CI")
        self.assertEqual(evt.component, "build")
        self.assertEqual(evt.event_type, "PIPELINE_FAILURE")
        self.assertEqual(evt.severity, "HIGH")
        self.assertEqual(evt.message, "Pipeline build : FAILED")

    def test_pipeline_ok(self):
        evt = normaliser_pipeline({**PIPELINE, "status": "success"}, 7)
        self.assertEqual(evt.event_type, "PIPELINE_OK")
        self.assertEqual(evt.severity, "LOW")

    def test_cle_manquante(self):
        with self.assertRaises(ValueError):
            normaliser_pipeline({"job": "build", "date": "x"}, 1)


if __name__ == "__main__":
    unittest.main()