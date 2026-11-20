"""Pilotage des notebooks Kaggle via le CLI officiel (`python -m kaggle`).

Commandes exposées : pull, push, status, output, auth-check.
AUCUNE commande de soumission (`competitions submit`) n'est exposée : ce repo ne soumet jamais.
"""
import json
import subprocess
import sys
from pathlib import Path

from .config import kaggle_env


def _run(args: list, cwd=None) -> str:
    cmd = [sys.executable, "-m", "kaggle", *args]
    proc = subprocess.run(cmd, cwd=cwd, env=kaggle_env(), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"kaggle {' '.join(args)} a échoué :\n{proc.stdout}{proc.stderr}")
    return proc.stdout


def auth_check() -> str:
    # Appel léger qui exige une authentification valide.
    return _run(["competitions", "list", "-s", "physical-engineering"])


def pull(kernel_ref: str, out_dir: Path) -> str:
    """Télécharge un notebook public ou privé (owner/slug) avec son métadonnée."""
    out_dir.mkdir(parents=True, exist_ok=True)
    return _run(["kernels", "pull", kernel_ref, "-p", str(out_dir), "-m"])


def write_metadata(folder: Path, kernel_slug: str, title: str, code_file: str,
                   competition: str | None, gpu: bool, internet: bool) -> Path:
    """Crée kernel-metadata.json pour un push. kernel_slug = 'pseudo/nom-du-notebook'."""
    folder.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": kernel_slug,
        "title": title,
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": gpu,
        "enable_internet": internet,
        "dataset_sources": [],
        "competition_sources": [competition] if competition else [],
        "kernel_sources": [],
    }
    path = folder / "kernel-metadata.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def push(folder: Path) -> str:
    """Pousse le notebook du dossier et lance son exécution sur Kaggle."""
    if not (folder / "kernel-metadata.json").exists():
        raise SystemExit(f"kernel-metadata.json absent dans {folder}")
    return _run(["kernels", "push", "-p", str(folder)])


def status(kernel_ref: str) -> str:
    return _run(["kernels", "status", kernel_ref])


def output(kernel_ref: str, out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    return _run(["kernels", "output", kernel_ref, "-p", str(out_dir)])
