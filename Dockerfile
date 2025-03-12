FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Copie du reste des fichiers
COPY . .
ENV PYTHONPATH=/app

EXPOSE 5000

# Création des buckets S3 via LocalStack
CMD aws --endpoint-url=http://localstack:4566 s3 mb s3://raw && \
    aws --endpoint-url=http://localstack:4566 s3 mb s3://staging && \
    aws --endpoint-url=http://localstack:4566 s3 mb s3://curated && \
    python src/app.py
