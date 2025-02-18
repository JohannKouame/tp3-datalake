from datasets import load_dataset
import boto3

# Configurer le client S3 avec vos credentials
bucket_name = "raw"
s3_client = boto3.client(
    's3',
    aws_access_key_id='root',  # Remplacez par votre Access Key
    aws_secret_access_key='root',  # Remplacez par votre Secret Key
    endpoint_url="http://localhost:4566"
)

# Lister les dossiers
print(f"Listing folders in bucket: {bucket_name}")
response = s3_client.list_objects_v2(Bucket=bucket_name, Delimiter='/')

if 'CommonPrefixes' in response:
    for prefix in response['CommonPrefixes']:
        print(prefix['Prefix'])  # Affiche chaque dossier
else:
    print("No folders found in the bucket.")
    