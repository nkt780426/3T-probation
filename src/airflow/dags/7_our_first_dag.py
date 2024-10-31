from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'vohoang',
    'retries': 5,
    'retry_delay': timedelta(seconds=10)
}


with DAG(
    dag_id='our_first_dag_v5',
    default_args=default_args,
    description='This is our first dag that we write',
    start_date=datetime(2021, 7, 29, 2),
    schedule_interval='@daily',
    catchup=False,
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command='echo "Hello my son. I\'m your dad."'
    )
    
    task2 = BashOperator(
        task_id='seccond_task',
        bash_command='echo "hey, I am task2 and will be running after task 1"'
    )
    
    task3 = BashOperator(
        task_id='third_task',
        bash_command='echo "hey, I am task3 and will be running after task 1"'
    )
    
    # Build dependence giữa các task để tạo thành Dag hoàn chỉnh
    # C1:
    # task1.set_downstream(task2)
    # task1.set_downstream(task3)
    # C2:
    # task1 >> task2
    # task1 >> task3
    # C3:
    task1 >> [task2, task3]