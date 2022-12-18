from airflow import Dataset
from airflow.decorators import dag, task
import pendulum

default_args = {
    'owner': 'airflow',
}

example_dataset = Dataset( name="dataset",
    description="A dataset",
    dataset_type="dataset",
    dataset_uri="s3://trino.minio-service/warehouse/dwh"
    dataset_format="avro")

@dag(default_args=default_args, 
     schedule=example_dataset, 
     tags=["ETL"]
)
def test_dataset_dag():
    @task
    def test_dataset_task1():
        print(example_dataset)
