from airflow import Dataset
from airflow.decorators import dag, task
import pendulum

default_args = {
    'owner': 'airflow',
}

example_dataset = Dataset("s3://trino.minio-service/warehouse/dwh")

@dag(default_args=default_args, 
     schedule=example_dataset, 
     tags=["ETL"]
)
def test_dataset_dag():
    @task
    def test_dataset_task1():
        print(example_dataset)
