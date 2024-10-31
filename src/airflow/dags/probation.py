from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'vohoang',
    'retries': 3,
    'retry_delay': timedelta(seconds=10)
}

with DAG(
    dag_id='probation_v1',
    default_args=default_args,
    description='Hello my son',
    start_date=datetime.now(),
    schedule_interval='0 7 * * 1-6',
    catchup=False,
    max_active_runs=1
) as dag:
    task1 = BashOperator(
        task_id='move_cache_to_minio',
        bash_command="cd /app/move_cache_to_minio && python3 main.py"
    )
    
    task2 = BashOperator(
        task_id='batch_sync_mysql',
        bash_command="cd /app/batch_sync_mysql && python3 main.py"
    )
    task1 >> task2