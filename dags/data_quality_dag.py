from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

SODA_CFG = "/usr/local/airflow/soda/configuration.yml"
SODA_CHK = "/usr/local/airflow/soda/checks.yml"

with DAG(
    dag_id="data_quality_dag",
    start_date=datetime(2025, 9, 15),
    schedule="@daily",
    catchup=False,
    tags=["quality","soda"],
):
    # Quick precheck: show module availability and files
    precheck = BashOperator(
        task_id="precheck",
        bash_command=(
            "python -c \"import importlib,sys; "
            "print('soda module:', 'OK' if importlib.util.find_spec('soda') else 'MISSING'); "
            "import pkgutil; print('packages:', [m.name for m in pkgutil.iter_modules() if m.name.startswith('soda')][:5])\" && "
            f"ls -l {SODA_CFG} && ls -l {SODA_CHK}"
        ),
    )

    # Call Soda via Python module (no reliance on 'soda' shell entrypoint)
    scan = BashOperator(
        task_id="soda_scan",
        bash_command=(
            f"python -m soda.scan -v -d postgres {SODA_CFG} {SODA_CHK}"
        ),
    )

    precheck >> scan
