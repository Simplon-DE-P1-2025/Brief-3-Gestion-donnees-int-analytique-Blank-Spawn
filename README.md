# Brief-3-Gestion-donnees-int-analytique-Blank-Spawn
Gestion centralisée de données et interface analytique interactive.

## 📋 Contexte
Projet de centralisation et visualisation des données pour le département de surveillance et sauvetage. Le système intègre un pipeline ETL robuste, une validation de données stricte et une interface utilisateur complète avec CRUD et dashboards analytiques.

## 🎯 Objectifs
- ✅ Récupérer et nettoyer les données
- ✅ Centraliser dans une base de données (PostgreSQL)
- ✅ Créer une interface CRUD et des dashboards analytiques (Streamlit)
- ✅ Valider les données (Pandera)
- ✅ Documenter et tester (Pytest)
- ✅ Orchestrer avec Docker/Docker Compose

## 🛠️ Stack technique
- **Backend**: Python 3.9+
- **Validation**: Pandera
- **Interface**: Streamlit
- **Base de données**: PostgreSQL
- **Orchestration**: Docker & Docker Compose
- **Tests**: Pytest
- **Infrastructure**: Supabase (optionnel)

## 📁 Structure du projet

```
├── pipeline/                    # Pipeline ETL
│   ├── main.py                 # Point d'entrée du pipeline
│   ├── schemas/                # Schémas de validation Pandera
│   ├── utils/                  # Utilitaires (BD, types de données)
│   └── data/                   # Données d'entrée/sortie
├── streamlit_app/              # Application Streamlit
│   ├── 1_Home.py              # Page d'accueil
│   ├── pages/                 # Pages additionnelles (Dashboard, CRUD, Audit, Logs)
│   ├── utils/                 # Utilitaires (authentification, BDD, helpers)
│   ├── data_loader.py         # Chargement des données
│   ├── utils.py               # Fonctions utilitaires
│   └── visualizations.py      # Composants de visualisation
├── support_tools/              # Scripts de développement
│   ├── sql_scripts/           # Scripts SQL (tables, KPI, analyse)
│   └── *.py                   # Scripts d'import et nettoyage
├── tests/                      # Tests unitaires (Pytest)
├── docker-compose.yml          # Configuration Docker
├── requirements.txt            # Dépendances Python
└── README.md                   # Cette documentation

```

### Descriptions des répertoires

- **pipeline** - Pipeline ETL complet pour extraction, transformation et chargement des données
- **streamlit_app** - Application Streamlit avec interface utilisateur complète (accueil, dashboard, CRUD, audit, logs)
- **support_tools** - Scripts utilitaires pour développement et gestion des données
- **tests** - Suite de tests unitaires

## 🚀 Démarrage rapide

### 1. Prérequis
- Python 3.9 ou supérieur
- Docker et Docker Compose (optionnel)
- Git

### 2. Installation locale

#### Cloner le projet et installer les dépendances
```bash
# Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Configurer les variables d'environnement
Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Supabase (si utilisé)
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_clé_supabase

# Base de données PostgreSQL
user=postgres
password=votre_mot_de_passe
host=localhost
port=5432
dbname=nom_de_la_base
```

### 3. Lancer le pipeline ETL
```bash
python3 pipeline/main.py
```

### 4. Lancer l'application Streamlit
```bash
streamlit run streamlit_app/1_Home.py
```

L'application sera accessible sur `http://localhost:8501`

## 🐳 Utilisation avec Docker Compose

Pour une mise en place complète avec PostgreSQL en conteneur :

### Démarrer la base de données
```bash
docker-compose up -d
```

Cette commande lance un conteneur PostgreSQL avec les configurations définies dans le fichier `.env`.

### Vérifier le statut
```bash
docker-compose ps
```

### Arrêter la base de données
```bash
docker-compose down
```

### Arrêter et supprimer tous les volumes
```bash
docker-compose down -v
```

## 🚀 Lancement du projet en local

### Installation des dépendances
Avant de lancer les tests, assurez-vous d'installer les dépendances :
```bash
pip install -r requirements.txt
```

### Activation de l'environnement virtuel
Activez l'environnement virtuel Python :
```bash
source .venv/bin/activate
```

### Fichiers d'environnement
Le projet utilisant une base de données hébergée en ligne, nous utilisons des fichiers d'environnement pour stocker des variables nécessaires à la connexion en BDD.
Un premier fichier `.env` à placer à la racine du projet:

Les données nécessaires dans ces fichiers
- SUPABASE_URL= `URL de connexion à Supabase`
- SUPABASE_KEY= `clé Supabase`
- user= `utilisateur de base de données`
- password= `mot de passe utilisateur`
- host= `IP/Nom d'hôte pour la connexion à la base`
- port= `port de connexion`
- dbname= `nom de la base`

### Lancement
```bash
python3 pipeline/main.py
```

## 🐳 Lancement du projet avec Docker Compose

Pour utiliser Docker Compose afin de lancer la base de données PostgreSQL localement :

### Prérequis
- Docker et Docker Compose installés sur votre machine.
- Fichier `.env` configuré avec les variables d'environnement nécessaires (voir section "Fichiers d'environnement").

### Démarrage de la base de données
```bash
docker-compose up -d
```
Cette commande lance le conteneur PostgreSQL en arrière-plan. Le service sera accessible sur le port défini dans la variable `POSTGRES_PORT` du fichier `.env`.

### Arrêt de la base de données
```bash
docker-compose down
```
Cela arrête et supprime les conteneurs lancés par Docker Compose.

Après avoir démarré la base de données avec Docker Compose, vous pouvez lancer le pipeline comme indiqué dans la section "Lancement du projet en local".

## 📊 Accès à l'application

### Pages disponibles
1. **1_Home.py** - Page d'accueil et présentation
2. **2_Dashboard.py** - Dashboards analytiques
3. **3_Crud.py** - Gestion complète des données (Create, Read, Update, Delete)
4. **4_Audit.py** - Audit trail et historique des modifications
5. **5_Logs.py** - Logs du système et debugging

### Authentification
L'application inclut un système d'authentification basique. Consultez `streamlit_app/utils/auth_ui.py` pour les détails.

## 🗄️ Architecture de la base de données

La structure de la base est documentée dans le schéma :
<div align="center">
  <img src="assets/schema.png" alt="schema BDD" width="600">
</div>

Les scripts SQL de création sont disponibles dans `support_tools/sql_scripts/`.

## ✅ Tests et validation

### Exécuter tous les tests
```bash
pytest -v
```

### Tests avec rapport de couverture
```bash
pytest --cov=pipeline --cov-report=html --cov-report=term-missing
```

Le rapport HTML sera généré dans le dossier `htmlcov/`.

### Validation des données (Pandera)
Les schémas de validation Pandera sont définis dans `pipeline/schemas/schema_pandera.py`.

Ils garantissent l'intégrité des données lors du pipeline ETL.

## 📝 Workflow de développement

### Ajouter une nouvelle dépendance
```bash
pip install package_name
pip freeze > requirements.txt
```

### Créer une nouvelle page Streamlit
1. Créer un fichier dans `streamlit_app/pages/`
2. Respecter la convention de nommage : `N_NomPage.py`
3. Importer les composants nécessaires depuis `streamlit_app/utils/`

### Ajouter une validation Pandera
1. Définir le schéma dans `pipeline/schemas/schema_pandera.py`
2. L'utiliser dans `pipeline/main.py` pour valider les données

## 🐛 Dépannage

### Port déjà utilisé (8501)
```bash
streamlit run streamlit_app/1_Home.py --server.port 8502
```

### Erreurs de connexion à la base de données
- Vérifier que le fichier `.env` est correctement configuré
- S'assurer que Docker Compose est lancé si vous utilisez un conteneur PostgreSQL
- Vérifier les logs : `docker-compose logs postgres`

### Problèmes d'imports
Assurez-vous que l'environnement virtuel est activé et que les dépendances sont installées :
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 📚 Ressources

- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Pandera](https://pandera.readthedocs.io/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)

## 👥 Contribution

Avant de contribuer :
1. Créer une branche pour votre feature
2. Écrire des tests pour toute nouvelle fonctionnalité
3. Passer les tests et respecter la couverture de code
4. Soumettre une pull request

## 📄 Licence

[À compléter selon votre licence]

---
**Dernière mise à jour** : 15 janvier 2026