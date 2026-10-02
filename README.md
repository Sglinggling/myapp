# MyApp – Pipeline CI/CD vers Azure

Petite API Flask déployée automatiquement sur une VM Azure à chaque push sur `main`.

## L'application

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/` | GET | Page d'accueil |
| `/health` | GET | Healthcheck → `{"status": "ok"}` |
| `/items` | GET / POST | Lister / ajouter un article (`{"name": "...", "price": 10}`) |
| `/total` | GET | Total des prix des articles |

Lancer en local avec Docker :
```bash
docker build -t myapp .
docker run -d --name myapp -p 8016:8016 myapp
curl http://localhost:8016/health
```

## Tests

- **Unitaires** (Flask test client, sans serveur) : `pytest tests/unit`
- **E2E** (requêtes HTTP réelles sur le conteneur lancé) : `BASE_URL=http://localhost:8016 pytest tests/e2e`
  Ils vérifient la disponibilité (`/health`, `/`) et un parcours complet : ajout de 2 articles, lecture de la liste, vérification du total.

## Fonctionnement du pipeline

Déclenché automatiquement par un **`git push` sur `main`** (`.github/workflows/ci-cd.yml`), sans aucune action manuelle :

1. **Unit tests** : installation des dépendances et `pytest tests/unit`
2. **E2E tests** : build de l'image, démarrage du conteneur, `pytest tests/e2e`
3. **Build & Push** (uniquement si 1 et 2 sont OK) : build de l'image et push sur Docker Hub avec deux tags, `latest` et le SHA du commit
4. **Deploy** : connexion SSH à la VM Azure, `docker pull` de l'image du commit, puis redémarrage du conteneur `myapp`
5. **Vérification** : healthcheck sur la VM, puis depuis l'extérieur via l'IP publique (`http://<IP>:8016/health`)

Si un test échoue, le job s'arrête en erreur et les étapes suivantes ne sont pas lancées.

## Choix techniques

- **Flask + Gunicorn** : API simple, Gunicorn comme serveur de production dans le conteneur.
- **Tests E2E en pytest + requests** : même outil que les tests unitaires, testent l'application via HTTP comme un vrai client, sans dépendance lourde comme Cypress.
- **Tag par SHA de commit** : chaque déploiement correspond à une version précise et traçable. `latest` est fourni en plus par commodité.
- **Déploiement idempotent** : conteneur au nom fixe `myapp`, `docker rm -f myapp` puis `docker run`. Relancer le workflow ne crée jamais de doublon, et `--restart unless-stopped` relance l'appli si la VM redémarre.
- **Port** : l'appli écoute sur 8016 dans le conteneur, publiée sur le même port 8016 de la VM (port imposé).
- **Sécurité** : aucun identifiant dans le dépôt, tout passe par les GitHub Secrets :

| Secret | Contenu |
|---|---|
| `DOCKERHUB_USERNAME` | Identifiant Docker Hub |
| `DOCKERHUB_TOKEN` | Access token Docker Hub |
| `VM_HOST` | IP publique de la VM |
| `VM_USER` | Utilisateur SSH de la VM |
| `VM_SSH_KEY` | Clé privée SSH |
