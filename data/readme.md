<!-- after script creation -->
chmod +x download_data.sh
<!-- run script -->
sh download_data.sh "yes" "https://sagemaker.readthedocs.io/en/stable/" "sagemaker.readthedocs.io" "docs"
<!-- upload data into s3 -->
aws s3 cp --recursive docs/ s3://aws-rag/llm-rag/sagemaker.readthedocs.io/ --profile dustin-dev2-admin

