import logging
from datasets import load_dataset
from src.client.aws_s3 import S3
from src.logger.logger import Logger
from src.repository.aws_s3_repository import AwsS3Repository

LOGGING_VARIABLE = "[Data manager]"

Logger()
aws_s3 = AwsS3Repository(S3())

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
