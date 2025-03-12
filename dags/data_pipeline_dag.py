from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from src.command.manage_buckets import ingest_data

from src.repository.aws_s3_repository import AwsS3Repository
from src.client.aws_s3 import S3

aws_s3 = AwsS3Repository(S3())

def print_params_fn(**kwargs):
    import logging
    logging.info(kwargs)
    return None


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def process_to_raw():
    aws_s3.download_data("bucket_test")

def transform_raw_to_staging():
    aws_s3.transform_data(source_bucket="raw", target_bucket="staging")

def transform_staging_to_curated():
    aws_s3.transform_data(source_bucket="staging", target_bucket="curated")

with DAG(
    'data_lake_pipeline',
    default_args=default_args,
    description='Pipeline Airflow pour le Data Lake',
    schedule_interval='@daily',
    start_date=datetime(2024, 3, 1),
    catchup=False,
) as dag:

    start = BashOperator(
        task_id='start_pipeline',
        bash_command='echo "Pipeline démarré"',
    )

    raw_task = PythonOperator(
        task_id='process_to_raw',
        python_callable=ingest_data,  # La fonction à appeler
        op_kwargs={  # Les arguments à passer à la fonction
            'empty': False,
            'repo': 'Salesforce/wikitext',
            'dataset_name': 'wikitext-2-raw-v1',
            'bucket_name': 'raw'
        },
    )

    staging_task = PythonOperator(
        task_id='transform_raw_to_staging',
        python_callable=transform_raw_to_staging,
        provide_context=True
    )

    curated_task = PythonOperator(
        task_id='transform_staging_to_curated',
        python_callable=transform_staging_to_curated,
        provide_context=True
    )

    end = BashOperator(
        task_id='end_pipeline',
        bash_command='echo "Pipeline terminé"',
    )

    # Définir l'ordre des tâches
    start >> raw_task
