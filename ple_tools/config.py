"""Chargement des identifiants Kaggle.

Ordre de priorité :
1. variables d'environnement déjà définies (ex. `setx KAGGLE_API_TOKEN ...`)
2. fichier `.env` à la racine du repo (exclu de git)

Aucun secret n'est écrit dans le code. Seule la variable KAGGLE_API_TOKEN est utilisée.
L'ancien couple KAGGLE_USERNAME / KAGGLE_KEY (kaggle.json legacy) est refusé par l'API : on ne le passe pas.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def _read_dotenv(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def kaggle_env() -> dict:
    """Environnement à passer au CLI kaggle. Lève une erreur si le token manque."""
    env = dict(os.environ)
    if not env.get("KAGGLE_API_TOKEN"):
        env.update({k: v for k, v in _read_dotenv(ENV_FILE).items() if k == "KAGGLE_API_TOKEN"})
    if not env.get("KAGGLE_API_TOKEN"):
        raise SystemExit(
            "KAGGLE_API_TOKEN introuvable. Crée un token sur https://www.kaggle.com/settings/api "
            "puis mets-le dans un fichier .env (voir .env.example) ou dans une variable d'environnement."
        )
    # Évite qu'un ancien kaggle.json legacy prenne le pas sur le token.
    env.pop("KAGGLE_KEY", None)
    env.pop("KAGGLE_USERNAME", None)
    return env
