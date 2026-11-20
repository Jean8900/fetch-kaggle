# TODO — fetch-kaggle

## Gestion des secrets (bloquant)

- [ ] Générer un token API sur https://www.kaggle.com/settings/api (« Generate New Token »).
- [ ] Le placer dans `.env` (copie de `.env.example`) **ou** via `setx KAGGLE_API_TOKEN "..."`. Ne jamais le committer.
- [ ] Vérifier qu'il est bien ignoré : `git status --ignored` doit lister `.env`, et `git add -n .env` ne doit rien proposer.
- [ ] Ouvrir un nouveau terminal après `setx`.
- [ ] Lancer `python -m ple_tools auth-check`. Attendu : la liste des compétitions. Si 401, le token est faux ou révoqué.
- [ ] Ne jamais réutiliser l'ancien `kaggle.json` legacy : il est refusé par l'API (401).

## Validation du pilotage (après token)

- [ ] `auth-check` OK.
- [ ] `pull` d'un notebook public : vérifier le nom du dossier et la présence de `kernel-metadata.json`.
- [ ] `new-run` avec un notebook minimal (1 cellule `print`), `--gpu`, pseudo réel.
- [ ] `push` : vérifier que la syntaxe `kaggle kernels push -p` est acceptée par le CLI installé. Corriger `kernels.py` si besoin.
- [ ] `status` sur le run, puis `output` une fois terminé.
- [ ] Vérifier sur l'interface Kaggle que le notebook est bien privé et que le GPU est actif.

## Lecture de la compétition

- [ ] Résoudre la pagination de `list-notebooks` (onglet Code).
- [ ] Extraire les votes et la date de mise à jour des notebooks (pas seulement les liens).
- [ ] Remplacer le délai fixe de 6 s par `wait_for_selector` dans `pages.py`.
- [ ] Lire les notebooks publics (`pull`) et les télécharger pour analyse.
- [ ] Trouver où vivent les données de la compétition (repo GitHub du kit ? `google-research/ple` ?) : pas d'onglet Data sur la PLE.

## Garde-fous (à ne pas oublier)

- [ ] Aucune commande de soumission ne doit être ajoutée. La soumission reste manuelle.
- [ ] Les runs restent `is_private: true` et `enable_internet: false` par défaut.
- [ ] Pas de token dans le notebook ni dans les métadonnées poussées.

## Plus tard

- [ ] Tests automatisés (sans appel réseau) pour `config.py` et `write_metadata`.
- [ ] Commande `doctor` qui vérifie Python, Playwright, Chromium, CLI kaggle et token.
- [ ] Support de l'auth OAuth (`kaggle auth login`) si le token devient gênant.
