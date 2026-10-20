from src.contrat import Analyse, Evenement, PROCEDURES


def est_doublon(evt: Evenement, vus: set) -> bool:
    cle = (evt.timestamp, evt.source, evt.component,
           evt.event_type, evt.message)
    if cle in vus:
        return True
    vus.add(cle)
    return False


def compter_erreurs(evt: Evenement, compteur: dict) -> int:
    if evt.event_type == "LOG" and evt.severity in ["HIGH", "CRITICAL"]:
        compteur[evt.component] = compteur.get(evt.component, 0) + 1
        return compteur[evt.component]
    return 0


def chercher_procedures(evt: Evenement, base: dict) -> list:
    trouvees = []
    message_lower = evt.message.lower()
    for mot_cle, proc in base.items():
        if mot_cle.lower() in message_lower:
            trouvees.append(proc)
    return trouvees


def classifier(evt: Evenement, nb_erreurs: int = 0) -> str:
    if nb_erreurs >= 3:
        return "CRITICAL"
    return evt.severity


def analyser(evt: Evenement, base: dict, nb_erreurs: int = 0) -> Analyse:
    level = classifier(evt, nb_erreurs)
    procs = chercher_procedures(evt, base)

    explanation = " ".join(
        procs) if procs else "Cause inconnue : analyse manuelle requise"

    if evt.event_type == "VULNERABILITY":
        action = f"Mettre a jour la dependance {evt.component}"
    elif evt.event_type == "PIPELINE_FAILURE":
        action = f"Relancer le pipeline {evt.component}"
    elif level == "CRITICAL":
        action = f"Redemarrer le service {evt.component}"
    else:
        action = "Surveiller"

    sensitive = action.startswith("Redemarrer")
    evt.status = "ANALYZED"

    return Analyse(
        event_id=evt.id,
        level=level,
        explanation=explanation,
        action=action,
        sensitive=sensitive,
        sources=[evt.source]
    )
