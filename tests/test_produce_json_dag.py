# # tests/test_produce_json_dag.py
# import pytest
# from unittest.mock import patch

# def test_produce_json_called():
#     # patcher la référence utilisée PAR pipeline
#     with patch("dags.fusion_update_db_autonome.pipeline.__globals__['produce_JSON']") as mock_produce, \
#          patch("airflow.operators.python.PythonOperator"), \
#          patch("airflow.DAG"):

#         from dags import fusion_update_db_autonome

#         # appeler la pipeline originale
#         fusion_update_db_autonome.pipeline()

#         # vérifier que produce_JSON a bien été appelé
#         mock_produce.assert_called_once()
