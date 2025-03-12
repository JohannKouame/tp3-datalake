# Project Setup and Usage Guide

## Prerequisites
Ensure you have the following installed on your machine:
- Docker
- AWS CLI
- Python (with `pip`)
- LocalStack
- MongoDB

## 1. Initialize Docker Containers
Start the required services (LocalStack and MongoDB) using Docker Compose:

```bash
docker-compose up -d
```

## 2. Initialize and Run Apache Airflow
First, initialize Airflow:

```bash
docker-compose airflow-init
```

Then, build and start the Airflow containers:

```bash
docker compose up --build
```

## 3. API Usage with cURL
Interact with the services using the following cURL commands:

### Upload a File to Raw Bucket
```bash
curl -X PUT --data-binary @data.txt "http://localhost:4566/raw/data.txt"
```

### List Files in a Bucket
```bash
curl "http://localhost:4566/raw"
```

### Download a File from a Bucket
```bash
curl "http://localhost:4566/raw/data.txt" -o "downloaded_data.txt"
```
## 4. Accessing Docker Containers to Inspect Buckets

To access the Flask application container and inspect S3 bucket contents, execute the following:

```bash
docker exec -it tp3-datalake-flask-app-1 /bin/bash
```

Once inside the container, you can use AWS CLI to list or inspect files:

````bash
aws --endpoint-url=http://localstack:4566 s3 ls s3://raw
aws --endpoint-url=http://localstack:4566 s3 ls s3://staging
aws --endpoint-url=http://localstack:4566 s3 ls s3://curated
````
## 5. Notes
- Ensure LocalStack is running before performing AWS CLI operations.
- MongoDB and MySQL should be accessible and properly configured.
- Modify any endpoint URLs if different from defaults.
- Logs and debug information can be found in the corresponding Docker container logs.

---

This guide ensures a smooth setup and provides essential cURL commands for interacting with the system. For advanced configurations, please refer to the respective service documentation.
