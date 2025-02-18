import logging

from datasets import load_dataset
from src.client.aws_s3_client import S3
from tqdm import tqdm
from src.logger.logger import Logger
import click

LOGGING_VARIABLE = "[Data manager]"

Logger()

@click.command()
@click.option("--empty", default=False, type=click.BOOL, help="Put True if you want to empty bucket au lieu de les remplir")
@click.option("--repo", default="Salesforce/wikitext", help="Huggingface Repo where to find data")
@click.option("--dataset_name", default="wikitext-2-raw-v1", help="Specific dataset in the repo")
@click.option("--bucket_name", default="raw", help="Bucket name(s) where to store data. If many buckets, put them into bracket like a list.")
def manage_data(empty, repo: str, dataset_name: str, bucket_name: str):
    s3_client = S3()
    if empty:
        
        if type(bucket_name) is str:
            logging.info(msg=f"{LOGGING_VARIABLE} Empty bucket")
            
            # Si aucun fichier n'est précisé, on supprime tout le contenu du bucket
            response = s3_client.list_objects_v2(bucket_name)
            if 'Contents' in response:
                files_to_delete = [obj['Key'] for obj in response['Contents']]
                delete_objects = {'Objects': [{'Key': file} for file in files_to_delete]}
                s3_client.delete_objects(Bucket=bucket_name, Delete=delete_objects)
                print(f"{len(files_to_delete)} fichier(s) supprimé(s) du bucket {bucket_name}.")
            else:
                logging.info(msg=f"{LOGGING_VARIABLE} Bucket already empty.")
        elif type(bucket_name) is list:
            for bucket in bucket_name:
                logging.info(msg=f"{LOGGING_VARIABLE} Empty bucket")
                # Si aucun fichier n'est précisé, on supprime tout le contenu du bucket
                response = s3_client.list_objects_v2(bucket_name)
                if 'Contents' in response:
                    files_to_delete = [obj['Key'] for obj in response['Contents']]
                    delete_objects = {'Objects': [{'Key': file} for file in files_to_delete]}
                    s3_client.delete_objects(Bucket=bucket_name, Delete=delete_objects)
                    print(f"{len(files_to_delete)} fichier(s) supprimé(s) du bucket {bucket_name}.")
                else:
                    logging.info(msg=f"{LOGGING_VARIABLE} Bucket already empty.")
    else:
                # Charger les données WikiText
        logging.info(msg=f"{LOGGING_VARIABLE} Downloading data from HuggingFace...")
        data = load_dataset(repo, dataset_name)
        logging.info(msg=f"{LOGGING_VARIABLE} Data successfully downloaded.")

        logging.info(msg=f"{LOGGING_VARIABLE} Transferring data to S3 bucket...")
        # Parcourir chaque split et téléverser les données
        for split in ["train", "test", "validation"]:
            split_data = data[split]
            logging.info(msg=f"{LOGGING_VARIABLE} Transferring {split} data...")

            # Utiliser tqdm pour afficher une barre de progression
            for idx, unit in tqdm(enumerate(split_data), desc=f"Uploading {split}", total=split_data.num_rows):
                # Texte à téléverser
                text_data = unit['text']

                # Clé pour organiser les fichiers par split
                key = f"{split}/{split}_{idx}.txt"

                # Téléverser les données directement depuis la mémoire
                s3_client.put_object(bucket_name, key, text_data)

        logging.info(msg=f"{LOGGING_VARIABLE} Data successfully uploaded to the S3 bucket named 'raw'.")
        
        # Lister les dossiers
        logging.info(msg=f"Listing folders in bucket: {bucket_name}")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Delimiter='/')

        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                logging.info(msg=f"{LOGGING_VARIABLE} {prefix['Prefix']}")  # Affiche chaque dossier
        else:
            logging.info(msg=f"{LOGGING_VARIABLE} No folders found in the bucket.")

if __name__ == "__main__":
    manage_data()
    