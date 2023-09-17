#!/bin/bash

# Your AWS ECR Repository URL
ECR_REPOSITORY_URL="288344227581.dkr.ecr.ap-southeast-2.amazonaws.com/aws-rag-processing-job"

# In order to push your built image to private ecr
aws ecr get-login-password --region ap-southeast-2 --profile dustin-dev2-admin | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL

# Tag the image
docker build -t aws-rag-processing-job -f processing_job.Dockerfile .

# Tag the image
docker tag aws-rag-processing-job:latest $ECR_REPOSITORY_URL:latest

# Push to ECR
docker push $ECR_REPOSITORY_URL:latest