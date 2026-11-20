# fetch-kaggle

CLI Python qui pilote une compétition Kaggle depuis un terminal (ou depuis Claude Code) :
lire les onglets publics, lister et télécharger les notebooks, pousser un notebook sur Kaggle
avec GPU et récupérer ses sorties.

**Garde-fou : le repo ne soumet jamais de réponse.** Aucune commande `competitions submit`, aucune fonction d'envoi.
La soumission reste un geste manuel sur Kaggle.

Première cible : `physical-engineerings-last-exam` (Google, Agent Harness on PLE).

---

## 1. Architecture

```
ple_tools/
├── __main__.py   # python -m ple_tools  -> cli.main()
├── cli.py        # argparse, 8 sous-commandes, routage
├── config.py     # lecture du token (env ou .env), purge des vars legacy
├── pages.py      # Playwright : onglets publics -> out/<slug>/<onglet>.txt|png + index.json
└── kernels.py    # wrapper du CLI officiel `python -m kaggle` (pull/push/status/output)
```

| Partie | Techno | Auth requise |
|---|---|---|
| Lecture des onglets (`fetch-pages`, `list-notebooks`) | Playwright + Chromium headless | non (pages publiques rendues en JS) |
| Pilotage des notebooks (`pull`, `push`, `status`, `output`, `auth-check`) | `kaggle` 2.x CLI | oui, `KAGGLE_API_TOKEN` |

Pourquoi Playwright : les pages Kaggle sont rendues côté client. `curl` ne renvoie qu'une coquille HTML vide.

Dépendances (`requirements.txt`) : `kaggle>=2.2`, `playwright>=1.45`.

---

## 2. Installation

```powershell
cd C:\Users\jeanm\fetch-kaggle
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Python 3.10+ requis (testé avec 3.13).

---

## 3. Secrets (à faire une fois)

Le repo ne contient aucun secret. Trois éléments sont nécessaires :

| Élément | Où le trouver | Où le mettre |
|---|---|---|
| Token API Kaggle | https://www.kaggle.com/settings/api → « Generate New Token » | `.env` (variable `KAGGLE_API_TOKEN`) |
| Pseudo Kaggle | Ton profil Kaggle | à passer en argument (`pseudo/nom-du-notebook`) |
| Autorisation GPU / compétition | Accepter les règles de la compétition sur Kaggle | manuel, une fois |

### Pourquoi pas `kaggle.json` ?

L'ancien fichier `~/.kaggle/kaggle.json` (username + key) est refusé par l'API actuelle : `401 Unauthenticated`.
Le CLI 2.x attend un token au format `KAGGLE_API_TOKEN`. `config.py` retire donc aussi `KAGGLE_KEY` et `KAGGLE_USERNAME` de l'environnement passé au CLI, pour éviter qu'un ancien couple prenne le dessus.

### Option A : fichier `.env` (recommandé)

```powershell
copy .env.example .env
notepad .env        # remplacer coller_ici_le_token
```

`.env` est dans `.gitignore`. Vérifie avant chaque commit : `git status --ignored` ne doit pas le montrer en « to be committed ».

### Option B : variable d'environnement utilisateur

```powershell
setx KAGGLE_API_TOKEN "xxxx"
```

`setx` ne met à jour que les **nouveaux** terminaux. Ferme et rouvre le terminal (ou Claude Code) après.

### Ce qu'il ne faut jamais faire

- Coller le token dans un fichier versionné, un message de commit, un ticket ou le chat.
- Mettre le token dans `kernel-metadata.json` ou dans le notebook poussé : un notebook public le révèle.
- Faire `git add -f .env`.

---

## 4. Utilisation

```powershell
python -m ple_tools auth-check
python -m ple_tools fetch-pages physical-engineerings-last-exam
python -m ple_tools list-notebooks physical-engineerings-last-exam
python -m ple_tools pull avikdas567/code-gated-agent-harness-for-physical-engineering
python -m ple_tools new-run TONPSEUDO/mon-test-ple mon_notebook.ipynb --competition physical-engineerings-last-exam --gpu
python -m ple_tools push out\runs\TONPSEUDO__mon-test-ple
python -m ple_tools status TONPSEUDO/mon-test-ple
python -m ple_tools output TONPSEUDO/mon-test-ple
```

Sorties : `out/` (ignoré par git).
- `out/<slug>/` : textes, captures et `index.json` des onglets lus.
- `out/runs/<pseudo__slug>/` : dossier de push (notebook + `kernel-metadata.json`).
- `out/kernels/`, `out/outputs/` : notebooks et sorties téléchargés.

### Format de `kernel-metadata.json` (généré par `new-run`)

```json
{
  "id": "pseudo/nom-du-notebook",
  "title": "Nom affiché",
  "code_file": "mon_notebook.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": false,
  "dataset_sources": [],
  "competition_sources": ["physical-engineerings-last-exam"],
  "kernel_sources": []
}
```

`is_private: true` par défaut : un run ne doit pas être public sans décision explicite.
`enable_internet: false` par défaut : pas d'accès réseau depuis le notebook sauf demande.

---

## 5. État des tests

| Commande | Statut | Note |
|---|---|---|
| `--help` | OK | |
| `fetch-pages` | OK | 4/5 onglets sur la PLE ; `data` renvoie `not_found` (pas d'onglet Data) |
| `list-notebooks` | OK | 15 notebooks trouvés sur la première page |
| `new-run` | OK | génère le `kernel-metadata.json` |
| `auth-check` sans token | OK | message d'erreur explicite |
| `auth-check` avec token | **non testé** | attend un token valide |
| `pull`, `push`, `status`, `output` | **non testés** | attendent un token ; la syntaxe CLI est à valider au premier essai |

---

## 6. Limites connues

- `list-notebooks` ne lit que la première page de l'onglet Code (pas de pagination).
- Les votes des notebooks ne sont pas extraits (seuls les liens le sont).
- Le bouton « Download » de Kaggle ne fonctionne pas hors connexion : `pull` passe par le token.
- `fetch-pages` attend un délai fixe (6 s par onglet) : lent, mais simple. Un `wait_for_selector` serait plus rapide.
- Playwright ouvre Chromium headless : en cas de changement de l'interface Kaggle, les sélecteurs de texte peuvent casser.
- Le CLI kaggle 2.x a changé d'auth (OAuth via `kaggle auth login`). Ce repo utilise le token ; l'OAuth n'est pas géré.

---

## 7. Utiliser ce repo avec Claude Code (mode « Jarvis »)

1. Ouvre un terminal dans `C:\Users\jeanm\fetch-kaggle` et lance `claude`.
2. Claude lit `CLAUDE.md` (règles du repo) et ce README.
3. Demande en langage naturel : « fetch la compétition X », « pousse le notebook Y avec GPU », « donne-moi le statut du run »...

Claude Code exécute les commandes `python -m ple_tools ...`. Les règles sont dans `CLAUDE.md` : pas de soumission, pas de secret dans le code, pas de push public sans accord.

Voir `TODO.md` pour les étapes restantes.
