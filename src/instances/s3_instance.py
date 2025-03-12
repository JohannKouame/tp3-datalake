from src.client.aws_s3 import S3
from src.repository.aws_s3_repository import AwsS3Repository

s3_client = S3()
aws_s3 = AwsS3Repository(s3_client)