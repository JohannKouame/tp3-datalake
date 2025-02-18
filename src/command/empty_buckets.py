import boto3
import argparse

def delete_files_from_bucket(bucket_name, files=None):
    s3 = boto3.client("s3", endpoint_url="http://localhost:4566")  # Utilise l'endpoint local ou celui de ton instance AWS

    if files:
        for file in files:
            # Vérifie si le fichier existe avant de le supprimer
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=file)
            if 'Contents' in response:
                delete_objects = {'Objects': [{'Key': file}]}
                s3.delete_objects(Bucket=bucket_name, Delete=delete_objects)
                print(f"Le fichier {file} a été supprimé du bucket {bucket_name}.")
            else:
                print(f"Le fichier {file} n'existe pas dans le bucket {bucket_name}.")
    else:
        # Si aucun fichier n'est précisé, on supprime tout le contenu du bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            files_to_delete = [obj['Key'] for obj in response['Contents']]
            delete_objects = {'Objects': [{'Key': file} for file in files_to_delete]}
            s3.delete_objects(Bucket=bucket_name, Delete=delete_objects)
            print(f"{len(files_to_delete)} fichier(s) supprimé(s) du bucket {bucket_name}.")
        else:
            print(f"Le bucket {bucket_name} est vide.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supprimer des fichiers dans un bucket S3")
    parser.add_argument("--bucket", type=str, required=True, help="Nom du bucket S3")
    parser.add_argument("--files", type=str, nargs='*', help="Liste des fichiers à supprimer (séparés par des espaces). Si non précisé, supprime tout le bucket.")
    args = parser.parse_args()
    
    delete_files_from_bucket(args.bucket, args.files)