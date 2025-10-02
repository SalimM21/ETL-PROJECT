# dwh.py
from airflow.decorators import task

@task()
def staging_table():
    print("Mise à jour de la table staging")
    return "staging_done"

@task()
def core_table():
    print("Mise à jour de la table core")
    return "core_done"
