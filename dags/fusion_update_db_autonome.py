from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scripts.youtube_extract import run_extract

default_args = {"owner": "you", "retries": 2, "retry_delay": timedelta(minutes=3)}

with DAG(
    dag_id="produce_JSON",
    start_date=datetime(2025, 9, 15),
    schedule="@daily",      # ✅ use `schedule`
    catchup=False,
    default_args=default_args,
    tags=["youtube", "extract"],
):
    extract = PythonOperator(
        task_id="extract_youtube",
        python_callable=run_extract,
    )
