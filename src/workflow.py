from src import analyse, extraction, notification
from src.contrat import PROCEDURES


def _traiter(evt, vus, compteur, historique, base):
    if analyse.est_doublon(evt, vus):
        return None
    nb_erreurs = analyse.compter_erreurs(evt, compteur)
    ana = analyse.analyser(evt, base, nb_erreurs)
    notif = notification.notifier(evt, ana, historique)
    return {"evenement": evt, "analyse": ana, "notification": notif}


def traiter_log(ligne, numero, vus, compteur, historique, base=PROCEDURES):
    return _traiter(extraction.normaliser_log(ligne, numero), vus, compteur, historique, base)


def traiter_scan(rapport, numero, vus, compteur, historique, base=PROCEDURES):
    return _traiter(extraction.normaliser_scan(rapport, numero), vus, compteur, historique, base)


def traiter_pipeline(rapport, numero, vus, compteur, historique, base=PROCEDURES):
    return _traiter(extraction.normaliser_pipeline(rapport, numero), vus, compteur, historique, base)
