from unittest.mock import patch
import dags.data_quality_dag

def test_data_quality_dag_scan():
    with patch("airflow.operators.bash.BashOperator"), \
         patch("airflow.DAG"):
        dags.data_quality_dag.data_quality_dag()
        dags.data_quality_dag.data_quality_dag.assert_called_once()
