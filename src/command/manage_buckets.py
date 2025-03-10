import logging
from datasets import load_dataset
from src.client.aws_s3 import S3
from tqdm import tqdm
from src.logger.logger import Logger
import click
from src.repository.aws_s3_repository import AwsS3Repository

LOGGING_VARIABLE = "[Data manager]"

Logger()
@click.group()
def cli():
    """Command-line tool for data management."""
    pass


@click.command()
@click.option("--empty", default=False, type=click.BOOL, help="Put True if you want to empty bucket au lieu de les remplir")
@click.option("--repo", default="Salesforce/wikitext", help="Huggingface Repo where to find data")
@click.option("--dataset_name", default="wikitext-2-raw-v1", help="Specific dataset in the repo")
@click.option("--bucket_name", default="raw", help="Bucket name(s) where to store data. If many buckets, put them into bracket like a list.")
def manage_data(empty, repo: str, dataset_name: str, bucket_name: str):
    aws_s3 = AwsS3Repository(S3())
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
            
            logging.info(msg=f"{LOGGING_VARIABLE} Listing folders in bucket: {bucket_name}")
            response = aws_s3.list_files(Bucket=bucket_name, Delimiter="/")
            folders = aws_s3.list_folders(Bucket=bucket_name, folders=response['CommonPrefixes'])
            for folder, count in folders.items():
                logging.info(f"{LOGGING_VARIABLE} Folder : {folder} - File count: {count}")
        else:
            logging.info(msg=f"{LOGGING_VARIABLE} Error durinng uploading files to S3 bucket named {bucket_name}")
        # Listing folders
if __name__ == "__main__":
    cli()