from src.client.aws_s3 import S3
#import logging
from tqdm import tqdm
import traceback
import csv
import io

from airflow.utils.log.logging_mixin import LoggingMixin

logging = LoggingMixin().log

LOGGING_VARIABLE = "[AWS S3]"

class AwsS3Repository:
    def __init__(self, s3_client:S3):
        self.s3_client = s3_client

    def list_files(self, Bucket:str, Prefix:str="", Delimiter:str="") -> list:
        response = self.s3_client.list_objects_v2(Bucket=Bucket, Prefix=Prefix, Delimiter=Delimiter)

        return response

    def list_folders(self, Bucket:str, folders: dict) -> dict:
        response = {}
        for folder in folders:
            folder_name = folder['Prefix']

            folder_response = self.list_files(Bucket=Bucket, Prefix=folder_name)
            file_count = len(folder_response.get('Contents', []))
            response[folder_name] = file_count
        return response

    def process_data(self, Bucket, Prefix, process_func, to_staging=False, to_curated=False, dataset_type=None) -> dict:
        try:
            logging.info(msg=f"{LOGGING_VARIABLE} Getting list of {Bucket}'s files...")

            response = self.list_files(Bucket, Prefix)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            processed_data = {}
            all_tokens = []

            for file_key in files:
                logging.info(msg=f"{LOGGING_VARIABLE}📥 Download {file_key} from {Bucket}...")
                response = self.s3_client.get_object(Bucket=Bucket, Key=file_key)

                logging.info(msg=f"{LOGGING_VARIABLE}⚙️ Prétraitement du fichier {file_key}...")
                raw_text = response['Body'].read().decode('utf-8')
                clean_text = process_func(raw_text)
                processed_data[file_key] = clean_text

                if to_staging:
                    self.upload_processed_file(Bucket='staging', file_key=file_key, clean_text=clean_text)
                if to_curated:
                    all_tokens.extend(clean_text)

            if to_curated and dataset_type:
                self.upload_aggregated_tokens_to_csv(Bucket='curated', tokens=all_tokens, dataset_type=dataset_type)

            return processed_data
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error while processing data {Bucket} ... : {exception}")
            return None

    def upload_processed_file(self, Bucket, file_key, clean_text):
        try:
            logging.info(f"Uploading cleaned data for {file_key} to {Bucket}...")
            clean_text_encoded = ' '.join(clean_text).encode('utf-8') if isinstance(clean_text, list) else clean_text.encode('utf-8')
            self.s3_client.put_object(Bucket=Bucket, Key=file_key, Body=clean_text_encoded)
        except Exception as exception:
            logging.critical(f"Error while uploading {file_key} to {Bucket}...", extra={"error": exception})

    def upload_aggregated_tokens_to_csv(self, Bucket, tokens, dataset_type='train'):
        try:
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)

            for token in tokens:
                csv_writer.writerow([token])

            csv_content = csv_buffer.getvalue().encode('utf-8')
            s3_key = f'{dataset_type}.csv'

            logging.info(f"Uploading aggregated tokenized data to {Bucket}/{s3_key}...")
            self.s3_client.put_object(Bucket=Bucket, Key=s3_key, Body=csv_content)
            logging.info(f"Successfully uploaded aggregated data to {Bucket}/{s3_key}.")
        except Exception as exception:
            logging.critical(f"Error while uploading aggregated data to {Bucket}...", extra={"error": exception})


    def upload_files_into_one_folder(self, Bucket:str, Key:str, Body:str) -> bool:
        try:
            logging.info(f"{LOGGING_VARIABLE} 🚀 Uploading into {Bucket} ...")
            self.s3_client.put_object(Bucket=Bucket, Key=Key, Body=Body.encode('utf-8'))

            return True
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error while uploading data into {Bucket} ...", extra={"error":exception})
            return False

    def upload_files_into_multiple_folders_test(self, folders:list,
                                                data,
                                                Bucket:str) -> bool:
        try:
            logging.info(f"{LOGGING_VARIABLE} 🚀 Uploading into {Bucket} ...", extra={"folders": folders})
            for split in folders:
                split_data = data[split]
                logging.info(msg=f"{LOGGING_VARIABLE} Transferring {split} data...")
                logging.info(msg=f"{LOGGING_VARIABLE} split_data: {split_data}")
                for idx, unit in enumerate(list(split_data['text'][:100])):
                    logging.info(f"{LOGGING_VARIABLE} Unit: {unit}")
                    # Text to upload
                    text_data = unit
                    # Path
                    key = f"{split}/{split}_{idx}.txt"
                    # Transfer into bucket
                    logging.info(f"{LOGGING_VARIABLE} Uploading {text_data[:20]}... to {key}", extra={"key": key})
                    self.s3_client.put_object(Bucket=Bucket, Key=key, Body=text_data)

            return True
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error while uploading data into {Bucket} ...", extra={"error":exception,
                                                                                                        "traceback":traceback.format_exc()})

    def upload_files_into_multiple_folders(self, folders:list,
                                                data,
                                                Bucket:str) -> bool:
        try:
            logging.info(f"{LOGGING_VARIABLE} Uploading into {Bucket} ...")
            for split in folders:
                split_data = data[split]
                logging.info(msg=f"{LOGGING_VARIABLE} Transferring {split} data...")

                for idx, unit in tqdm(enumerate(split_data), desc=f"Uploading {split}", total=len(split_data.num_rows)):
                    # Text to upload
                    text_data = unit['text']
                    # Path
                    key = f"{split}/{split}_{idx}.txt"
                    # Transfer into bucket
                    self.s3_client.put_object(Bucket=Bucket, Key=key, Body=text_data)

            return True
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error while uploading data into {Bucket} ...", extra={"error":exception})
            return False

    def upload_consolidated_csv(self, Bucket, dataset_type, processed_data):
        """
        Consolidate tokenized data into a single CSV file and upload it to the specified S3 bucket.

        Args:
            Bucket (str): The S3 bucket name (e.g., 'curated').
            dataset_type (str): The dataset type ('train', 'test', 'validation').
            processed_data (dict): A dictionary where keys are file names and values are lists of tokens.
        """
        try:
            # Créer un fichier CSV en mémoire
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)

            # Écrire chaque token sur une ligne
            for file_key, tokens in processed_data.items():
                for token in tokens:
                    csv_writer.writerow([token])

            # Encoder le contenu CSV
            csv_content = csv_buffer.getvalue().encode('utf-8')

            # Définir le chemin du fichier dans le bucket S3
            s3_key = f'{dataset_type}.csv'

            logging.info(f"Uploading consolidated {dataset_type} data to {Bucket} as {s3_key}...")

            # Uploader le fichier consolidé dans S3
            self.s3_client.put_object(Bucket=Bucket, Key=s3_key, Body=csv_content)

            logging.info(f"Successfully uploaded consolidated {dataset_type} data to {Bucket}/{s3_key}.")

        except Exception as exception:
            logging.critical(f"Error while uploading consolidated {dataset_type} data to {Bucket}...", extra={"error": exception})
