# YouTube ELT Pipeline – Projet V4

## 🎯 Contexte
De nombreuses entreprises du secteur digital souhaitent automatiser l'analyse des performances de contenu YouTube pour optimiser leurs stratégies marketing et comprendre les tendances du marché.  
Ce projet a pour objectif de concevoir un **pipeline ELT complet** permettant d’extraire, transformer, charger et valider les données YouTube automatiquement.

## 👩‍💻 User Stories
- **Data Engineer** : Orchestrer l'extraction quotidienne des données YouTube via des DAGs Airflow.
- **Analyste de données** : Accéder aux données structurées dans PostgreSQL via pgAdmin, DBeaver ou Airflow.
- **DevOps** : Déployer et monitorer le pipeline via Docker et Astro CLI.
- **Data Quality Manager** : Valider automatiquement la qualité des données avec Soda Core.
- **Développeur** : Lancer le pipeline localement et le déployer avec GitHub Actions.
- **Business Analyst (bonus)** : Visualiser les données via un dashboard Streamlit.

## 🛠️ Technologies utilisées
- **Python** : Scripts ETL et DAGs Airflow
- **Apache Airflow & Astro CLI** : Orchestration et planification
- **PostgreSQL** : Data Warehouse avec schémas `staging` et `core`
- **Docker** : Containerisation
- **Soda Core** : Validation qualité des données
- **GitHub Actions** : CI/CD automatisé
- **Bonus** : Streamlit pour dashboard et multi-chaînes YouTube

## ⚙️ Architecture du pipeline
1. **DAG `produce_JSON`** :  
   - Extraction des données YouTube (video_id, titre, date, durée, vues, likes, commentaires)  
   - Gestion de la pagination et quotas API  
   - Sauvegarde en JSON horodaté  
   - Retry logic en cas d'erreurs

2. **DAG `update_db`** :  
   - Chargement des JSON dans le schéma `staging`  
   - Transformation et nettoyage des données  
   - Chargement en `core`  
   - Gestion des doublons et historique

3. **DAG `data_quality`** :  
   - Validation automatique avec Soda Core  
   - Tests de complétude, cohérence et format  
   - Alertes en cas d’anomalies

## 📝 Installation & usage
### Prérequis
- Docker et Docker Compose
- Astro CLI
- Clé API YouTube v3
- PostgreSQL

### Lancement du projet
```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/youtube-elt-pipeline.git
cd youtube-elt-pipeline

# Créer un fichier .env avec vos clés API
cp .env.example .env
# Éditer .env avec vos clés YouTube API

# Démarrer le projet Airflow avec Astro
astro dev start

# Si le build échoue à cause de timeouts réseau, essayer:
# 1. Attendre et relancer: astro dev start
# 2. Ou installer les dépendances optionnelles après le démarrage:
#    astro dev bash
#    python /opt/airflow/scripts/install_optional_deps.py

# Lancer les DAGs depuis l'UI Airflow
```

### Résolution des problèmes de build
Si vous rencontrez des timeouts lors de l'installation des dépendances Python:
1. Le fichier `requirements.txt` contient uniquement les dépendances essentielles
2. Les dépendances optionnelles (soda-core, streamlit, etc.) sont dans `requirements-optional.txt`
3. Vous pouvez les installer après le démarrage du container avec le script fourni

### CI/CD
- Workflow GitHub Actions : build Docker, tests unitaires et intégration, vérification DAGs.

### Validation qualité
- Soda Core vérifie row_count, cohérence et format des données
- Rapports automatiques disponibles dans les logs

### Bonus
- Dashboard Streamlit pour visualisation des vues, likes et commentaires
- Support multi-chaînes YouTube

## 📂 Structure du projet
```
youtube-elt-pipeline/
├─ dags/
│  ├─ produce_json.py
│  ├─ update_db.py
│  └─ data_quality.py
├─ modules/
│  └─ utils.py
├─ tests/
│  └─ test_pipeline.py
├─ docker/
│  └─ Dockerfile
├─ .github/workflows/ci.yml
└─ README.md
```

## ✅ Livrables
- Pipeline ELT opérationnel avec DAGs et validation qualité
- Dépôt GitHub structuré et documenté
- Captures d’écran Airflow, PostgreSQL et Soda Core
- (Bonus) Dashboard Streamlit et multi-chaînes YouTube

## 📚 Références utiles
- [YouTube Data API v3](https://developers.google.com/youtube/v3/docs)
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Astro CLI Docs](https://www.astronomer.io/docs/astro/cli/overview)
- [Soda Core Docs](https://docs.soda.io/soda-core/getting-started.html)
- [Docker Docs](https://docs.docker.com/get-started/)
- [Streamlit Docs](https://docs.streamlit.io/)

