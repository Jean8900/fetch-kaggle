# CLAUDE.md — règles pour Claude Code dans fetch-kaggle

Ce repo pilote des compétitions Kaggle depuis le terminal. Lis `README.md` et `TODO.md` avant d'agir.

## Règles absolues

1. **Ne jamais soumettre** une réponse à une compétition (`competitions submit`, équivalent, ou bouton). La soumission reste manuelle, faite par l'utilisateur sur Kaggle.
2. **Ne jamais écrire de secret** dans un fichier versionné, un message de commit, un notebook ou `kernel-metadata.json`. Le token vit dans `.env` (ignoré par git) ou dans `KAGGLE_API_TOKEN`.
3. **Ne jamais afficher le contenu de `.env`** ni le token dans la conversation. Pour vérifier, utilise `auth-check` (exit ≠ 0 = token absent ou refusé).
4. **Pas de `git add -f .env`**, ni de commit contenant `out/`.
5. **Pas de push public** de notebook ni de changement de `is_private` sans accord explicite de l'utilisateur.
6. **Pas d'accès réseau** dans un run (`enable_internet: false`) sauf demande explicite.

## Commandes

- Entrée unique : `python -m ple_tools <commande>` (voir `python -m ple_tools --help`).
- Lecture publique (sans token) : `fetch-pages`, `list-notebooks`.
- Pilotage (token requis) : `auth-check`, `pull`, `new-run`, `push`, `status`, `output`.

## Conventions

- Sorties dans `out/` uniquement.
- Une erreur sur un onglet ou un notebook n'interrompt pas les autres : logguer et continuer.
- Avant de lancer un `push` GPU (coûteux et visible), confirme le notebook et la compétition avec l'utilisateur, sauf consigne contraire explicite.
- Les règles de la compétition et les dates limites sont sur la page `rules` (`out/<slug>/rules.txt`), à relire avant toute action.

## Ce que tu ne sais pas encore

- La syntaxe exacte du CLI `kaggle kernels push` n'est pas validée sur ce poste. Vérifie-la au premier run et corrige `ple_tools/kernels.py` si besoin.
- L'emplacement des données de la compétition PLE n'est pas confirmé (pas d'onglet Data).
