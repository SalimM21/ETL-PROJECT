from airflow import DAG
from datetime import datetime
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="master_daily",
    start_date=datetime(2025, 9, 17),
    schedule="0 2 * * *",   # daily at 02:00 local. See Option B for timezone.
    catchup=False,
    tags=["orchestration"],
):
    kick_extract = TriggerDagRunOperator(
        task_id="run_produce_json",
        trigger_dag_id="produce_JSON"
    )

    kick_load = TriggerDagRunOperator(
        task_id="run_update_db",
        trigger_dag_id="update_db"
    )

    kick_quality = TriggerDagRunOperator(
        task_id="run_data_quality",
        trigger_dag_id="data_quality"
    )

    kick_extract >> kick_load >> kick_quality
