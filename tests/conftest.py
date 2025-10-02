# tests/conftest.py
import sys
from unittest.mock import MagicMock

# === Mock global pour Airflow et ses sous-modules utilisés ===
sys.modules['airflow'] = MagicMock()
sys.modules['airflow.models'] = MagicMock()
sys.modules['airflow.settings'] = MagicMock()
sys.modules['airflow.operators.python'] = MagicMock()
sys.modules['airflow.operators.bash'] = MagicMock()
sys.modules['airflow.decorators'] = MagicMock()
sys.modules['airflow.providers.postgres.hooks.postgres'] = MagicMock()
sys.modules['airflow.operators.trigger_dagrun'] = MagicMock()
sys.modules['airflow.exceptions'] = MagicMock()
sys.modules['airflow.hooks'] = MagicMock()
sys.modules['airflow.hooks.base'] = MagicMock()

# === Mock du package `dags` ===
sys.modules['dags'] = MagicMock()

# === Mock des modules internes des DAGs ===
# On crée des modules vides pour que les importations dans les tests réussissent
sys.modules['dags.data_quality_dag'] = MagicMock()
sys.modules['dags.fusion_update_db_autonome'] = MagicMock()
sys.modules['dags.update_db_dag'] = MagicMock()

# === Import du package `dags` après le mock ===
# import dags

# === Attacher uniquement les mocks de fonctions qui seront patchées par les tests ===
# Ces mocks seront remplacés par patch() dans les tests
# dags.fusion_update_db_autonome.produce_JSON = MagicMock(name="produce_JSON")
# dags.update_db_dag.ensure_tables = MagicMock(name="ensure_tables")
# dags.update_db_dag.load_latest_json = MagicMock(name="load_latest_json")
