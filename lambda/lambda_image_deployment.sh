#!/bin/bash

# Your AWS ECR Repository URL
ECR_REPOSITORY_URL="288344227581.dkr.ecr.ap-southeast-2.amazonaws.com/aws-rag-lambda"

# Authenticate to ECR
# https://stackoverflow.com/questions/69274998/could-not-connect-to-the-endpoint-url-https-api-ecr-public-xxxxxxxxx-amazona
# if you are going to deal with the ecr-public service, you must work with the us-east-1 region, here you need to log in public ecr as well to pull a public aws lambda python image
aws ecr-public get-login-password --region us-east-1 --profile dustin-dev2-admin | docker login --username AWS --password-stdin public.ecr.aws
# In order to push your built image to private ecr
aws ecr get-login-password --region ap-southeast-2 --profile dustin-dev2-admin | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL

# Build Docker image
docker build -t aws-rag-lambda -f lambda.Dockerfile .

# Tag the image
docker tag aws-rag-lambda:latest $ECR_REPOSITORY_URL:latest

# Push to ECR
docker push $ECR_REPOSITORY_URL:latest

# Remove the local image
docker rmi $ECR_REPOSITORY_URL:latest