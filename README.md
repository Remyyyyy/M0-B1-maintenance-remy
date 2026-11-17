# FastIA — Service de criticité maintenance prédictive

API REST qui prédit la **criticité d'un incident machine** (`basse`, `moyenne`, `haute`)
à partir de mesures capteurs et d'historique, grâce à un modèle scikit-learn pré-entraîné.

## 🏗️ Architecture

```
app/
├── main.py       # API FastAPI : routes /health et /predict, chargement du modèle, logs
└── schemas.py    # Schémas Pydantic : validation des entrées / format des sorties
model/
├── model.joblib       # Modèle entraîné (pipeline StandardScaler + OneHotEncoder + RandomForest)
└── train_baseline.py  # Script d'entraînement
tests/
├── test_health.py     # Tests de /health
└── test_predict.py    # Tests de /predict (cas valide, erreur 422, 5 types de machine)
logs/                  # Logs de l'API (créé automatiquement, non versionné)
Dockerfile             # Image de production
```

**Fonctionnement d'une requête `/predict` :**

1. FastAPI reçoit le JSON et Pydantic le valide (sinon → erreur 422).
2. Les données sont converties en DataFrame pandas.
3. Le modèle (chargé une seule fois au démarrage) prédit la classe et les probabilités.
4. L'API renvoie `{"criticite": ..., "probabilites": {...}}`.
5. Chaque requête est journalisée avec Loguru (entrée, sortie, durée en ms) dans `logs/api.log`
   (rotation 5 Mo, rétention 7 jours, compression zip).

**Stack :** FastAPI · Pydantic · scikit-learn · pandas · Loguru · pytest · Docker

## 🚀 Lancer le service

### En local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

### Avec Docker

```bash
docker build -t fastia-maintenance:dev .
docker run --rm -p 8000:8000 fastia-maintenance:dev
```

### Exemple d'appel

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"type_machine": "compresseur", "age_machine_jours": 1500, "derniere_maintenance_jours": 45,
       "temperature_moyenne": 68.5, "vibration_moyenne": 3.2, "pression_moyenne": 7.8,
       "nb_incidents_3_mois": 2}'
```

Réponse :

```json
{"criticite": "basse", "probabilites": {"basse": 0.945, "haute": 0.0, "moyenne": 0.055}}
```

## 🧪 Tester

```bash
python -m pytest -v
```

9 tests : 2 sur `/health`, 7 sur `/predict` (cas valide, type de machine invalide → 422,
test paramétré sur les 5 types de machine).

## ✅ Preuves

### 1. Tests — `pytest -v`

```console
$ python -m pytest -v
======================== test session starts ========================
platform linux -- Python 3.11.18, pytest-8.3.4, pluggy-1.7.0 -- /home/rrauflet/miniconda3/envs/cisia/bin/python
cachedir: .pytest_cache
rootdir: /home/rrauflet/formation/M0-B1-maintenance-remy
plugins: Faker-40.52.0, platformdirs-4.14.5, anyio-4.6.2.post1
collected 9 items

tests/test_health.py::test_health_returns_200 PASSED                  [ 11%]
tests/test_health.py::test_health_response_schema PASSED              [ 22%]
tests/test_predict.py::test_predict_valid_returns_200 PASSED          [ 33%]
tests/test_predict.py::test_predict_invalid_type_machine_returns_422 PASSED [ 44%]
tests/test_predict.py::test_predict_all_machine_types[pompe] PASSED   [ 55%]
tests/test_predict.py::test_predict_all_machine_types[compresseur] PASSED [ 66%]
tests/test_predict.py::test_predict_all_machine_types[convoyeur] PASSED [ 77%]
tests/test_predict.py::test_predict_all_machine_types[presse] PASSED  [ 88%]
tests/test_predict.py::test_predict_all_machine_types[four] PASSED    [100%]

========================= 9 passed in 4.83s =========================
```

### 2. Santé du service dans le conteneur — `curl /health`

Conteneur lancé avec `docker run --rm -p 8000:8000 fastia-maintenance:dev`, puis depuis l'hôte :

```console
$ curl http://localhost:8000/health
{"status":"ok","model_loaded":true}
```

### 3. Image Docker — `docker images`

```console
$ docker images fastia-maintenance
IMAGE                    ID             DISK USAGE   CONTENT SIZE    EXTRA
fastia-maintenance:dev   8b5dcc669664   791MB        180MB             U
```
