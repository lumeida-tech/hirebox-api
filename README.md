# HireBox API

REST API pour la plateforme de recrutement HireBox. Construite avec [Litestar](https://litestar.dev/), PostgreSQL et Docker.

---

## Stack technique

| Composant   | Technologie                        |
|-------------|------------------------------------|
| Framework   | Litestar (ASGI)                    |
| Serveur     | Gunicorn + UvicornWorker           |
| Base de données | PostgreSQL 16                  |
| Driver async | asyncpg                           |
| Validation  | Pydantic v2                        |
| Config      | pydantic-settings + `.env`         |
| Docs        | Scalar (auto-générée)              |

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose v2
- Pas besoin de Python en local pour faire tourner l'API

---

## Démarrage rapide

### 1. Configurer l'environnement

```bash
cp .env.example .env
```

Modifier `.env` si besoin (les valeurs par défaut fonctionnent en dev) :

```env
POSTGRES_USER=hirebox
POSTGRES_PASSWORD=hirebox
POSTGRES_DB=hirebox

SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Lancer les services

```bash
docker compose up --build
```

Cela démarre :
- **api** → `http://localhost:8000`
- **db** → PostgreSQL sur `localhost:5432`

> L'API attend que PostgreSQL soit healthy avant de démarrer (healthcheck automatique).

### 3. Vérifier que l'API tourne

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "HireBox API"}
```

### 4. Accéder à la documentation interactive

Ouvrir `http://localhost:8000/docs` dans le navigateur (Scalar UI).

---

## Commandes utiles

```bash
# Lancer en arrière-plan
docker compose up -d --build

# Voir les logs de l'API
docker compose logs -f api

# Voir les logs de la base
docker compose logs -f db

# Arrêter les services
docker compose down

# Arrêter et supprimer les données PostgreSQL
docker compose down -v

# Rebuilder l'image uniquement
docker compose build api
```

---

## Structure du projet

```
api/
├── app.py                  # Point d'entrée Litestar
├── config/
│   └── settings.py         # Configuration via variables d'environnement
├── core/
│   ├── dependencies.py     # Dépendances partagées (DB session, user courant)
│   └── exceptions.py       # Exceptions métier + handlers HTTP
├── features/
│   ├── auth/               # Authentification (register, login)
│   ├── jobs/               # Offres d'emploi
│   ├── applications/       # Candidatures
│   ├── candidates/         # Profils candidats
│   └── companies/          # Entreprises
├── tests/
├── Dockerfile
├── compose.yml
├── requirement.txt
└── .env.example
```

Chaque feature suit la même structure interne :

```
feature/
├── controller.py   # Routes HTTP (Litestar Controller)
├── service.py      # Logique métier
├── schemas.py      # Schémas Pydantic (request / response)
└── exceptions.py   # Exceptions spécifiques à la feature
```

---

## Endpoints

### Health
| Méthode | Route     | Description        |
|---------|-----------|--------------------|
| GET     | /health   | Statut de l'API    |

### Auth
| Méthode | Route           | Description              |
|---------|-----------------|--------------------------|
| POST    | /auth/register  | Créer un compte          |
| POST    | /auth/login     | Connexion, retourne JWT  |

### Jobs
| Méthode | Route           | Description                        |
|---------|-----------------|------------------------------------|
| GET     | /jobs           | Lister les offres (paginé)         |
| GET     | /jobs/{id}      | Détail d'une offre                 |
| POST    | /jobs           | Créer une offre                    |
| PATCH   | /jobs/{id}      | Modifier une offre                 |
| DELETE  | /jobs/{id}      | Supprimer une offre                |

### Applications
| Méthode | Route                          | Description                     |
|---------|--------------------------------|---------------------------------|
| POST    | /applications                  | Postuler à une offre            |
| GET     | /applications/{id}             | Détail d'une candidature        |
| GET     | /applications/jobs/{job_id}    | Candidatures pour une offre     |
| PATCH   | /applications/{id}/status      | Mettre à jour le statut         |
| DELETE  | /applications/{id}/withdraw    | Retirer sa candidature          |

### Candidates
| Méthode | Route                  | Description                   |
|---------|------------------------|-------------------------------|
| GET     | /candidates            | Lister les candidats (paginé) |
| GET     | /candidates/{id}       | Profil d'un candidat          |
| POST    | /candidates/me         | Créer/mettre à jour son profil |

### Companies
| Méthode | Route              | Description                      |
|---------|--------------------|----------------------------------|
| GET     | /companies         | Lister les entreprises (paginé)  |
| GET     | /companies/{id}    | Détail d'une entreprise          |
| POST    | /companies         | Créer une entreprise             |
| PATCH   | /companies/{id}    | Modifier une entreprise          |
| DELETE  | /companies/{id}    | Supprimer une entreprise         |

---

## Variables d'environnement

| Variable                    | Défaut                      | Description                        |
|-----------------------------|-----------------------------|------------------------------------|
| `APP_ENV`                   | `development`               | Environnement (`development`, `production`) |
| `DEBUG`                     | `false`                     | Mode debug                         |
| `POSTGRES_USER`             | `hirebox`                   | Utilisateur PostgreSQL             |
| `POSTGRES_PASSWORD`         | `hirebox`                   | Mot de passe PostgreSQL            |
| `POSTGRES_DB`               | `hirebox`                   | Nom de la base de données          |
| `SECRET_KEY`                | `change-me-in-production`   | Clé secrète JWT                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440`                    | Durée de vie du token (en minutes) |

> En Docker, `DATABASE_URL` est construit automatiquement par le `compose.yml` à partir des variables `POSTGRES_*`. Pas besoin de le définir manuellement.

---

## Développement local (sans Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt

# Avec une instance PostgreSQL locale tournant sur le port 5432
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## Tests

```bash
# Dans le conteneur
docker compose exec api pytest

# En local
pytest
```
