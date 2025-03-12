import logging
from datasets import load_dataset
from src.client.aws_s3 import S3
from src.repository.aws_s3_repository import AwsS3Repository
from src.logger.logger import Logger
from src.utils.process_from_raw_to_staging import Processor
from src.utils.text_processor import TextProcessor
from src.instances.s3_instance import aws_s3

LOGGING_VARIABLE = "[Data manager]"

Logger()
#aws_s3 = AwsS3Repository(S3())
aws_s3 = aws_s3
processor = Processor()

def ingest_data(empty=False, repo="Salesforce/wikitext", dataset_name="wikitext-2-raw-v1", bucket_name="raw"):
    global aws_s3

    if empty:
        pass
    else:
        # Upload files
        logging.info(msg=f"{LOGGING_VARIABLE} Downloading data from HuggingFace...")
        data = load_dataset(repo, dataset_name)
        split = ["train", "test", "validation"]
        logging.info(msg=f"{LOGGING_VARIABLE} Data successfully downloaded.")

        # Browse each split and transfer data
        logging.info(msg=f"{LOGGING_VARIABLE} Transferring data to S3 bucket...")
        response = aws_s3.upload_files_into_multiple_folders_test(Bucket=bucket_name, data=data, folders=split)
        if response:
            logging.info(msg=f"{LOGGING_VARIABLE} Data successfully uploaded to the S3 bucket named {bucket_name}")

            # Listing folders
            logging.info(msg=f"{LOGGING_VARIABLE} Listing folders in bucket: {bucket_name}")
            response = aws_s3.list_files(Bucket=bucket_name, Delimiter="/")
            folders = aws_s3.list_folders(Bucket=bucket_name, folders=response['CommonPrefixes'])
            for folder, count in folders.items():
                logging.info(f"{LOGGING_VARIABLE} Folder : {folder} - File count: {count}")
        else:
            logging.critical(msg=f"{LOGGING_VARIABLE} Error during uploading files to S3 bucket named {bucket_name}")

def process_to_staging(bucket_name, prefix):
    global aws_s3
    logging.info(f"{LOGGING_VARIABLE} Prefix(s) : {prefix}")
    for p in prefix:
        logging.info(f"{LOGGING_VARIABLE} Processessing data from : {p}")
        processed_data = aws_s3.process_data(
            Bucket=bucket_name, 
            Prefix=p, 
            to_staging=True,
            to_curated=False,
            process_func=TextProcessor.clean_text)
        if processed_data:
            logging.info(f"{LOGGING_VARIABLE} Data processed successfully.")

            logging.info(msg=f"{LOGGING_VARIABLE} Listing folders in bucket: {bucket_name}")
            response = aws_s3.list_files(Bucket=bucket_name, Delimiter="/")
            folders = aws_s3.list_folders(Bucket=bucket_name, folders=response['CommonPrefixes'])
            for folder, count in folders.items():
                logging.info(f"{LOGGING_VARIABLE} Folder : {folder} - File count: {count}")
    else:
        logging.error(f"{LOGGING_VARIABLE} Data processing failed.")

def process_to_curated(bucket_name, prefix):
    global aws_s3
    logging.info(f"{LOGGING_VARIABLE} Prefix(s) : {prefix}")

    for p in prefix:
        logging.info(f"{LOGGING_VARIABLE} Processing data from: {p}")

        # Utilisation de process_data pour tokeniser le texte et uploader dans curated
        processed_data = aws_s3.process_data(
            Bucket=bucket_name,
            Prefix=p,
            to_staging=False,
            to_curated=True,
            process_func=TextProcessor.tokenize_text
        )

        if processed_data:
            logging.info(f"{LOGGING_VARIABLE} Data processed successfully.")

            logging.info(msg=f"{LOGGING_VARIABLE} Listing folders in bucket: {bucket_name}")
            response = aws_s3.list_files(Bucket=bucket_name, Delimiter="/")
            folders = aws_s3.list_folders(Bucket=bucket_name, folders=response['CommonPrefixes'])

            # Enregistrement des dossiers et du nombre de fichiers traités
            for folder, count in folders.items():
                logging.info(f"{LOGGING_VARIABLE} Folder: {folder} - File count: {count}")

            # Uploader les données dans un seul CSV par dataset (train/test/validation)
            dataset_type = p.split('/')[-1]  # Déterminer le type du dataset à partir du préfixe
            aws_s3.upload_consolidated_csv(Bucket='curated', dataset_type=dataset_type, processed_data=processed_data)
        else:
            logging.error(f"{LOGGING_VARIABLE} Data processing failed for prefix: {p}")

