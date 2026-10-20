from src.contrat import Analyse, Evenement, Notification


def choisir_canal(niveau: str) -> str:
    canaux = {
        "CRITICAL": "TEAMS",
        "HIGH": "SLACK",
        "MEDIUM": "EMAIL",
        "LOW": "DASHBOARD",
    }
    if niveau not in canaux:
        raise ValueError(f"Niveau inconnu : {niveau}")
    return canaux[niveau]


def rediger(evt: Evenement, analyse: Analyse) -> str:
    lignes = [
        f"[{analyse.level}] Composant : {evt.component}",
        f"Evenement : {evt.message}",
        f"Explication : {analyse.explanation}",
        f"Action proposee : {analyse.action}",
        f"Sources : {', '.join(analyse.sources)}",
    ]
    return "\n".join(lignes)


def notifier(evt: Evenement, analyse: Analyse, historique: list) -> Notification:
    notif = Notification(
        event_id=evt.id,
        channel=choisir_canal(analyse.level),
        recipient="equipe-ops",
        text=rediger(evt, analyse),
    )
    historique.append(notif)
    evt.status = "NOTIFIED"
    return notif


def valider_action(analyse: Analyse, reponse: str) -> bool:
    raise NotImplementedError


def tracer_decision(analyse: Analyse, approuve: bool, acteur: str,
                    journal: list, horodatage: str) -> dict:
    raise NotImplementedError
