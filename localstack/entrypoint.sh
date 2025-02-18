#!/bin/sh

# Attendre que le service S3 soit prêt
until awslocal s3 ls > /dev/null 2>&1; do
    echo "Waiting for LocalStack S3 to be ready..."
    sleep 1
done

echo "[] Creating S3 buckets..."

echo "Creating raw"
awslocal s3 mb s3://raw
echo "Done"

echo "Creating staging"
awslocal s3 mb s3://staging
echo "Done"

echo "Creating curated"
awslocal s3 mb s3://curated
echo "Done"

echo "S3 buckets created!"
exec "$@"
