#!/bin/bash

# Your AWS ECR Repository URL
ECR_REPOSITORY_URL="288344227581.dkr.ecr.ap-southeast-2.amazonaws.com/aws-rag"

# Authenticate to ECR
# https://stackoverflow.com/questions/69274998/could-not-connect-to-the-endpoint-url-https-api-ecr-public-xxxxxxxxx-amazona
# if you are going to deal with the ecr-public service, you must work with the us-east-1 region.
# aws ecr get-login-password --region ap-southeast-2 --profile dustin-dev2-admin | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL
aws ecr get-login-password --region ap-southeast-2 --profile dustin-dev2-admin | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL

# Build Docker image
docker build -t aws-rag-lambda -f lambda.Dockerfile .

# Tag the image
docker tag aws-rag-lambda:latest $ECR_REPOSITORY_URL:latest

# Push to ECR
docker push $ECR_REPOSITORY_URL:latest
