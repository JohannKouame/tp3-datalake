import boto3
import os

class S3:
    def __init__(self):
        self.client = boto3.client(
        's3',
        aws_access_key_id = os.getenv("AWS_S3_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url = os.getenv("ENDPOINT_URL")
    )

    def put_object(self, bucket_name:str, key:str, body):
        try:
            result = self.client.put_object(Bucket=bucket_name,
                                            Key=key,
                                            Body=body)
            return result
        except Exception as exception:
            raise exception
        
    def list_objects_v2(self, bucket_name: str):
        self.client.list_objects_v2(Bucket=bucket_name)