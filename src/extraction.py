"""Agent 1 : Extraction. Collecte et normalise les evenements (logs, scans, pipelines)."""
import re
from src.contrat import Evenement
_MOTIF_SECRET = re.compile(
    r"\b(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)[^\s&,;]+",
    re.IGNORECASE,
)
_MOTIF_BEARER = re.compile(r"(Bearer\s+)\S+", re.IGNORECASE)
_SEVERITES_LOG = {
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
    "ERROR": "HIGH",
    "WARN": "MEDIUM",
    "WARNING": "MEDIUM",
}
_SEVERITES_SCAN = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


def _identifiant(numero: int) -> str:
    return f"EVT-{numero:05d}"


def _verifier_cles(rapport: dict, cles: tuple) -> None:
    manquantes = [c for c in cles if c not in rapport]
    if manquantes:
        raise ValueError(f"Cle(s) manquante(s) : {', '.join(manquantes)}")


def masquer_secrets(texte: str) -> str:
    texte = _MOTIF_SECRET.sub(r"\1\2[SECRET]", texte)
    return _MOTIF_BEARER.sub(r"\1[SECRET]", texte)


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    champs = ligne.split(maxsplit=4)
    if len(champs) < 5:
        raise ValueError(
            f"Ligne de log invalide (moins de 5 champs) : {ligne!r}")
    date, heure, niveau, composant, message = champs
    return Evenement(
        id=_identifiant(numero),
        timestamp=f"{date}T{heure}Z",
        source=source,
        component=composant,
        environment=environment,
        event_type="LOG",
        severity=_SEVERITES_LOG.get(niveau.upper(), "LOW"),
        message=masquer_secrets(message),
    )


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("cve", "package", "severity", "date"))
    severite = str(rapport["severity"]).upper()
    if severite not in _SEVERITES_SCAN:
        severite = "LOW"
    return Evenement(
        id=_identifiant(numero),
        timestamp=rapport["date"],
        source="TRIVY",
        component=rapport["package"],
        environment=environment,
        event_type="VULNERABILITY",
        severity=severite,
        message=f"Vulnerabilite {rapport['cve']} dans {rapport['package']}",
    )


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("job", "status", "date"))
    echec = str(rapport["status"]).lower() == "failed"
    return Evenement(
        id=_identifiant(numero),
        timestamp=rapport["date"],
        source="CI",
        component=rapport["job"],
        environment=environment,
        event_type="PIPELINE_FAILURE" if echec else "PIPELINE_OK",
        severity="HIGH" if echec else "LOW",
        message=f"Pipeline {rapport['job']} : {rapport['status']}",
    )
