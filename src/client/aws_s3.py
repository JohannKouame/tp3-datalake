import boto3
import os
#import logging
from airflow.utils.log.logging_mixin import LoggingMixin

logging = LoggingMixin().log

LOGGING_VARIABLE = "[S3 Client]"
class S3:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id = "root",
            aws_secret_access_key = "root",
            endpoint_url = "http://localstack:4566"
        )
        try:
            response = self.client.list_buckets()
            logging.info(f"{LOGGING_VARIABLE} Buckets: {response['Buckets']}")
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error : {exception}")

    def put_object(self, Bucket:str, Key:str, Body):
        try:
            result = self.client.put_object(Bucket=Bucket,
                                            Key=Key,
                                            Body=Body)
            return result
        except Exception as exception:
            logging.critical(f"{LOGGING_VARIABLE} Error : {exception}")
            raise exception

    def get_object(self, Bucket:str, Key:str):
        return self.client.get_object(Bucket=Bucket, Key=Key)

    def list_objects_v2(self, Bucket: str, Delimiter: str="", Prefix: str=""):
        return self.client.list_objects_v2(Bucket=Bucket, Prefix=Prefix, Delimiter=Delimiter)
