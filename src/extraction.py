from src.contrat import Evenement


def masquer_secrets(texte: str) -> str:
    raise NotImplementedError


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    raise NotImplementedError
