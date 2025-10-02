# # tests/test_update_db_dag.py
# import pytest
# from unittest.mock import patch

# def test_update_db_pipeline_called():
#     with patch("dags.update_db_dag.ensure_tables") as mock_ensure, \
#          patch("dags.update_db_dag.load_latest_json") as mock_load, \
#          patch("airflow.operators.python.PythonOperator"), \
#          patch("airflow.DAG"):

#         from dags import update_db_dag

#         # appeler la pipeline originale
#         update_db_dag.pipeline()

#         mock_ensure.assert_called_once()
#         mock_load.assert_called_once()
