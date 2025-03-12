from flask import Flask, jsonify
import logging
from src.client.aws_s3 import S3
from src.repository.aws_s3_repository import AwsS3Repository
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from src.instances.s3_instance import aws_s3

app = Flask(__name__)

# Configuration de l'accès AWS
#s3_client = AwsS3Repository(S3())
s3_client = aws_s3


LOGGING_VARIABLE = "[FLASK APP]"

# Buckets S3 à utiliser
RAW_BUCKET = 'raw'
STAGING_BUCKET = 'staging'
CURATED_BUCKET = 'curated'


@app.route('/raw', methods=['GET'])
def get_raw_data():
    try:
        # Message dans les logs pour vérifier que la requête est bien reçue
        print("Request received for '/raw' endpoint")
        
        # Récupération des fichiers depuis le bucket
        files = list_files("raw")
        
        # Si des fichiers sont trouvés, on retourne une réponse avec les fichiers
        if files:
            return jsonify({"message": "Request processed successfully", "files": files}), 200
        else:
            return jsonify({"message": "No files found", "files": files}), 200
    except Exception as e:
        # Si une erreur se produit, on log l'erreur et on retourne un message d'erreur
        logging.error(f"Error fetching raw data: {e}")
        return jsonify({"error": "Failed to fetch raw data", "message": str(e)}), 500



@app.route('/staging', methods=['GET'])
def get_staging_data():
    try:
        files = list_files("staging")
        return jsonify({"files": files}), 200
    except Exception as e:
        logging.error(f"Error fetching staging data: {e}")
        return jsonify({"error": "Failed to fetch staging data"}), 500


@app.route('/curated', methods=['GET'])
def get_curated_data():
    try:
        files = list_files("curated")
        return jsonify({"files": files}), 200
    except Exception as e:
        logging.error(f"Error fetching curated data: {e}")
        return jsonify({"error": "Failed to fetch curated data"}), 500


# Simple test of connectivity to S3
@app.route('/health', methods=['GET'])
def health_check():
    try:
        s3_client.list_buckets()
        return jsonify({"status": "ok"}), 200
    except (NoCredentialsError, PartialCredentialsError):
        logging.error(f"{LOGGING_VARIABLE} Invalid AWS credentials.")
        return jsonify({"status": "error", "message": "Invalid credentials"}), 500
    except Exception as e:
        logging.error(f"Error checking health: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Get number of file for the buckets
@app.route('/stats', methods=['GET'])
def stats():
    try:
        raw_count = get_bucket_file_count("raw")
        staging_count = get_bucket_file_count("staging")
        curated_count = get_bucket_file_count("curated")

        return jsonify({
            "raw_count": raw_count,
            "staging_count": staging_count,
            "curated_count": curated_count
        }), 200
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return jsonify({"error": "Failed to fetch stats"}), 500

# Get files from a specific bucket
def list_files(bucket_name):
    global s3_client
    """Récupère la liste des fichiers dans le bucket."""
    try:
        response = s3_client.list_files(Bucket=bucket_name)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return files
    except Exception as e:
        logging.error(f"Error listing files in {bucket_name}: {e}")
        return []


def get_bucket_file_count(bucket_name):
    """Récupère le nombre de fichiers dans un bucket."""
    global s3_client
    try:
        files = s3_client.list_files(Bucket= bucket_name)
        return len(files["files"])
    except Exception as e:
        logging.error(f"Error counting files in {bucket_name}: {e}")
        return 0


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
