import os
from datetime import datetime

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from includes.etl_slack_script import (extract_data, extract_user_list,
                                       load_data_to_postgres,
                                       load_user_list_to_postgres)

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
    def extract_data_from_slack_timesheet():
        file_path = extract_data()
        return file_path
    
    @task
    def extract_data_from_slack_user_list():
        file_path = extract_user_list()
        return file_path
    
    @task
    def validate_file_exist(file_path):
        assert os.path.exists(file_path)
        return file_path

    @task
    def validate_user_list_exist(file_path):
        assert os.path.exists(file_path)
        return file_path

    @task
    def load_data_timesheet(file_path):
        load_data_to_postgres(file_path)
        
        return file_path

    @task
    def load_data_users_list(file_path):
        load_user_list_to_postgres(file_path)
        return file_path
    
    dbt_test = BashOperator(
        task_id= "dbt_test",
        bash_command="cd /git/repo/sql-dbt/sql-dbt && dbt ls && dbt test"
    )
    
    dbt_run = BashOperator(
        task_id= "dbt_run",
        bash_command="cd /git/repo/sql-dbt/sql-dbt && dbt ls && dbt seed && dbt run "
    )
    
    re_data_run = BashOperator(
        task_id= "re_data_run",
        bash_command="cd /git/repo/sql-dbt/sql-dbt && dbt run -m package:re_data"
    )
    
    re_data_overview_generate = BashOperator(
        task_id= "re_data_overview_generate",
        bash_command="cd /git/repo/sql-dbt/sql-dbt && re_data overview generate"
    )
    
    SLACK_WEBHOOK = Variable.get("SLACK_WEBHOOK")
    
    notify_data_anomalies = BashOperator(
        task_id="notify_data_anomalies",
        bash_command=f"""cd /git/repo/sql-dbt/sql-dbt && re_data notify slack \
            --webhook-url {SLACK_WEBHOOK}
        """
        
    )
        
    
    extract_data_from_slack_timesheet = extract_data_from_slack_timesheet()
    extract_data_from_slack_user_list = extract_data_from_slack_user_list()
    validate_file_exist = validate_file_exist(extract_data_from_slack_timesheet)
    validate_user_list_exist = validate_user_list_exist(extract_data_from_slack_user_list)
    load_data_timesheet = load_data_timesheet(validate_file_exist)
    load_data_users_list = load_data_users_list(validate_user_list_exist)
    [load_data_timesheet, load_data_users_list ] >> dbt_run >> dbt_test >> re_data_run >> re_data_overview_generate >> notify_data_anomalies
    

etl_timesheet = etl_timesheet()