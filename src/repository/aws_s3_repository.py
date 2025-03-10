from src.client.aws_s3 import S3
import logging
from tqdm import tqdm
import traceback

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

    def process_data(self, Bucket, Prefix, process_func) -> dict:
        try:
            logging.info(msg=f"{LOGGING_VARIABLE} Getting list of {Bucket}'s files...")
            files = self.list_files(Bucket, Prefix)
            processed_data = {}

            for file_key in files:
                logging.info(msg=f"{LOGGING_VARIABLE}📥 Download {file_key} from {Bucket}...")
                response = self.s3_client.get_object(Bucket=Bucket, Key=file_key)

                logging.info(msg=f"{LOGGING_VARIABLE}⚙️ Prétraitement du fichier {file_key}...")
                raw_text = response['Body'].read().decode('utf-8')
                clean_text = process_func(raw_text)
                processed_data[file_key] = clean_text

            return  processed_data
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error while processing data {Bucket} ...", extra={"error":exception})
            return None

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
                logging.info(msg=f"{LOGGING_VARIABLE} Transferring {split} data...", extra={"split_data": split_data})
                for idx, unit in tqdm(enumerate(list(split_data['text'][:100])), desc=f"Uploading {split}", total=100):
                    # Text to upload
                    text_data = unit
                    # Path
                    key = f"{split}/{split}_{idx}.txt"
                    # Transfer into bucket
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
