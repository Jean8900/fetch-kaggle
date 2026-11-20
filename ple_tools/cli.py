"""Point d'entrée : `python -m ple_tools <commande>`.

  fetch-pages <slug>                 lit les onglets publics (overview, data, code, discussion, rules)
  list-notebooks <slug>              liste les notebooks visibles dans l'onglet Code
  pull <owner/notebook> [--out DIR]  télécharge un notebook (via token)
  new-run <owner/notebook-slug> <fichier.ipynb> [--competition SLUG] [--gpu] [--internet] [--title T]
                                     prépare un dossier de push avec kernel-metadata.json
  push <dossier>                     pousse et lance le notebook sur Kaggle
  status <owner/notebook>            statut du dernier run
  output <owner/notebook> [--out DIR] récupère les sorties
  auth-check                         vérifie que le token est accepté

Pas de commande de soumission : ce repo ne soumet jamais une réponse à une compétition.
"""
import argparse
import json
import sys
from pathlib import Path

from . import kernels
from .pages import fetch_tabs_sync, TABS
from .config import ROOT

OUT = ROOT / "out"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ple_tools", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("fetch-pages")
    p.add_argument("slug")
    p.add_argument("--tabs", nargs="+", choices=list(TABS), default=None)

    p = sub.add_parser("list-notebooks")
    p.add_argument("slug")

    p = sub.add_parser("pull")
    p.add_argument("ref")
    p.add_argument("--out", type=Path, default=None)

    p = sub.add_parser("new-run")
    p.add_argument("kernel_slug", help="pseudo/nom-du-notebook")
    p.add_argument("notebook", type=Path)
    p.add_argument("--competition", default=None)
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--internet", action="store_true")
    p.add_argument("--title", default=None)

    p = sub.add_parser("push")
    p.add_argument("folder", type=Path)

    p = sub.add_parser("status")
    p.add_argument("ref")

    p = sub.add_parser("output")
    p.add_argument("ref")
    p.add_argument("--out", type=Path, default=None)

    sub.add_parser("auth-check")

    a = ap.parse_args(argv)

    if a.cmd == "fetch-pages":
        res = fetch_tabs_sync(a.slug, OUT / a.slug, a.tabs)
        print(json.dumps({k: v.get("status") for k, v in res.items()}, ensure_ascii=False))
    elif a.cmd == "list-notebooks":
        res = fetch_tabs_sync(a.slug, OUT / a.slug, ["code"])
        for nb in res.get("code", {}).get("notebooks", []):
            print(nb["ref"], nb["url"])
    elif a.cmd == "pull":
        out = a.out or (OUT / "kernels" / a.ref.replace("/", "__"))
        print(kernels.pull(a.ref, out))
        print(f"-> {out}")
    elif a.cmd == "new-run":
        title = a.title or a.kernel_slug.split("/")[-1].replace("-", " ").title()
        folder = OUT / "runs" / a.kernel_slug.replace("/", "__")
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / a.notebook.name
        target.write_bytes(a.notebook.read_bytes())
        meta = kernels.write_metadata(folder, a.kernel_slug, title, a.notebook.name,
                                      a.competition, a.gpu, a.internet)
        print(f"Dossier de push prêt : {folder} ({meta.name})")
    elif a.cmd == "push":
        print(kernels.push(a.folder))
    elif a.cmd == "status":
        print(kernels.status(a.ref))
    elif a.cmd == "output":
        out = a.out or (OUT / "outputs" / a.ref.replace("/", "__"))
        print(kernels.output(a.ref, out))
        print(f"-> {out}")
    elif a.cmd == "auth-check":
        print(kernels.auth_check())
    return 0


if __name__ == "__main__":
    sys.exit(main())
