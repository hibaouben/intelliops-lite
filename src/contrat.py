from dataclasses import dataclass

NIVEAUX = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Base de procedures (runbooks, recherche simplifiee) : mot-cle -> procedure
PROCEDURES = {
    "oomkilled": "Conteneur arrete faute de memoire : augmenter la limite memoire.",
    "pipeline": "Echec de pipeline : lire les logs du job puis relancer apres correction.",
    "vulnerabilite": "Vulnerabilite : mettre a jour la dependance vers une version corrigee.",
}


@dataclass
class Evenement:
    id: str
    timestamp: str
    source: str        # DOCKER, TRIVY ou CI
    component: str
    environment: str   # dev, test ou production
    event_type: str    # LOG, VULNERABILITY, PIPELINE_FAILURE ou PIPELINE_OK
    severity: str
    message: str
    status: str = "NEW"  # NEW -> ANALYZED -> NOTIFIED


@dataclass
class Analyse:
    event_id: str
    level: str
    explanation: str
    action: str
    sensitive: bool
    sources: list


@dataclass
class Notification:
    event_id: str
    channel: str
    recipient: str
    text: str
