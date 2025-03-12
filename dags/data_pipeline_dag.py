from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from src.command.manage_buckets import ingest_data
from src.command.manage_buckets import process_to_staging
from src.command.manage_buckets import process_to_curated

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
        python_callable=process_to_staging,
        op_kwargs={  # Les arguments à passer à la fonction
            'bucket_name': 'raw',
            'prefix': ["test", "train", "validation"]
        },
    )

    curated_task = PythonOperator(
        task_id='transform_staging_to_curated',
        python_callable=process_to_curated,
        op_kwargs={  # Les arguments à passer à la fonction
            'bucket_name': 'staging',
            'prefix': ["test", "train", "validation"]
        },
    )

    end = BashOperator(
        task_id='end_pipeline',
        bash_command='echo "Pipeline terminé"',
    )

    # Définir l'ordre des tâches
    start >> raw_task >> staging_task >> curated_task >> end
