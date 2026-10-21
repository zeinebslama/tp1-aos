# tp1-aos

# BiblioTech — Lab 1 : du monolithe aux services SOAP & REST

## Structure
- `biblioTech.py` : Partie 1, monolithe (SQLAlchemy + PyQt5)
- `soap/soap_service.py` : Partie 2, service SOAP (Spyne), WSDL dans `bibliotech.wsdl`
- `soap/rest_api.py` : Partie 3, API REST (FastAPI), documentation OpenAPI sur `/docs`
- `soap/models.py`, `soap/database.py`, `soap/schemas.py` : accès aux données et validation
- `tests/` : tests pytest (SOAP et REST)

## Prérequis
Python 3.11 (Spyne ne fonctionne pas sur 3.12+), Docker et Docker Compose.

## Lancer le projet
    python -m venv .venv && .venv\Scripts\activate
    pip install -r requirements.txt
    docker compose up -d db
    python -m app.init_db
    python -m app.soap_service              # SOAP : http://localhost:8000/?wsdl
    uvicorn app.rest_api:app --port 8001    # REST : http://localhost:8001/docs
    python -m pytest -v                     # tests (SQLite, sans toucher à Postgres)

API REST en conteneur : `docker compose up -d --build` (port 8001).

## Partie 1 — Limites de l'approche monolithique
- Interface, logique métier et accès aux données sont mélangés dans un seul script : difficile à lire, à tester et à faire évoluer.
- Un seul client possible : seule l'application PyQt5 peut utiliser les données ; une application web ou mobile devrait tout réécrire.
- Pas de contrat d'interface : les autres équipes ne savent pas comment utiliser le système sans lire le code.
- Une modification (par exemple le schéma de la base) impacte tout le script ; le déploiement est tout ou rien.
- Mise à l'échelle impossible par composant, et la validation n'existe que dans l'interface locale.
- Couplage fort à Python et à PyQt5 : aucun client dans un autre langage.

## Partie 2 — SOAP : plus de structure et de contrats
- **Contrat formel (WSDL)** : le service décrit ses opérations, ses types et ses erreurs dans un document lisible par machine ; le monolithe n'a que du code.
- **Typage fort** : le schéma XML impose des entiers, des réels et des champs obligatoires ; une requête invalide (`id` = "abc") est rejetée avant d'atteindre la logique.
- **Séparation des responsabilités** : le service ne connaît que les données et la logique ; le client est libre (web, mobile, autre langage) et génère son code à partir du WSDL.
- **Enveloppe et erreurs standardisées** : les erreurs sont des `Fault` structurés (`Client.NotFound`, `Client.InvalidCopies`...) au lieu d'exceptions Python locales.
- **Validation côté serveur** : stock et tarif négatifs, ID invalides sont refusés pour tous les clients, en plus des contraintes CHECK de la base.
- Contrepartie : plus verbeux (XML), plus lourd à écrire et à déboguer.

## Partie 3 — SOAP vs REST
| Critère | SOAP | REST |
|---|---|---|
| Lisibilité | XML verbeux, enveloppes à écrire à la main | JSON court, ressources et verbes HTTP (`GET /books`, `DELETE /books/1`) |
| Facilité d'utilisation | Nécessite un outil (Postman) ou un client généré | Utilisable avec un navigateur, curl ou n'importe quel client HTTP |
| Contrat / documentation | WSDL (strict, généré) | OpenAPI/Swagger généré automatiquement, avec interface d'essai |
| Validation | Schéma XML + code | Modèles Pydantic, erreurs 422 détaillées |
| Erreurs | `Fault` SOAP dans le corps de la réponse | Codes HTTP standards (404, 409, 422) |
| Intégration | Adapté aux systèmes d'entreprise et aux standards WS-* | Idéal pour le web et le mobile, facile à mettre en cache |
| Performance | Messages plus lourds | Messages plus légers et plus rapides à analyser |

Conclusion : SOAP convient quand un contrat strict et des standards d'entreprise sont requis ; REST est plus simple, plus léger et mieux adapté aux clients modernes web et mobiles.