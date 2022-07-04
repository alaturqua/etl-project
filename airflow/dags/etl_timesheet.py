import os
from datetime import datetime

import pendulum
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from includes.etl_slack_script import extract_data, load_data_to_postgres
from airflow.models import Variable


from airflow import DAG

default_args = {
    'owner': 'airflow',
}

@dag(default_args=default_args, 
     schedule_interval="@daily", 
     start_date=pendulum.datetime(2022,6,29),
     catchup=True,
     tags=["ETL"]
)
def etl_timesheet():
    """
    ### ETL Job to load data
    Load data to postgres.
    """
    
    @task
    def extract_data_from_slack():
        file_path = extract_data()
        return file_path
    
    @task
    def validate_file_exist(file_path):
        assert os.path.exists(file_path)
        return file_path

    @task
    def load_data(file_path):
        load_data_to_postgres(file_path)
        
        return file_path
    
    dbt_test = BashOperator(
        task_id= "dbt_test",
        bash_command="cd /dwh/sql-dbt && dbt ls && dbt test"
    )
    
    dbt_run = BashOperator(
        task_id= "dbt_run",
        bash_command="cd /dwh/sql-dbt && dbt ls && dbt seed && dbt run "
    )
    
    re_data_run = BashOperator(
        task_id= "re_data_run",
        bash_command="cd /dwh/sql-dbt && dbt run -m package:re_data"
    )
    
    re_data_overview_generate = BashOperator(
        task_id= "re_data_overview_generate",
        bash_command="cd /dwh/sql-dbt && re_data overview generate"
    )
    
    SLACK_WEBHOOK = Variable.get("SLACK_WEBHOOK")
    
    notify_data_anomalies = BashOperator(
        task_id="notify_data_anomalies",
        bash_command=f"""cd /dwh/sql-dbt && re_data notify slack \
            --webhook-url {SLACK_WEBHOOK}
        """
        
    )
        
    
    extract_data_from_slack = extract_data_from_slack()
    validate_file_exist = validate_file_exist(extract_data_from_slack)
    load_data = load_data(validate_file_exist)
    load_data >> dbt_test >> dbt_run >> re_data_run >> re_data_overview_generate >> notify_data_anomalies
    

etl_timesheet = etl_timesheet()