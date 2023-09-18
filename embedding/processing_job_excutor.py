import boto3
import logging
from sagemaker.processing import ScriptProcessor, ProcessingInput
import time
from sagemaker.session import Session


logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

#  fetch environmental value from aws parameter store
session = boto3.Session(profile_name='dustin-dev2-admin',  region_name='ap-southeast-2')
ssm = session.client('ssm')
sagemaker_session = Session(boto_session=session)
region = ssm.get_parameter(Name='REGION', WithDecryption=True)['Parameter']['Value']
processing_job_image_uri = ssm.get_parameter(Name='PROCESSING_JOB_IMAGE_URI', WithDecryption=True)['Parameter']['Value']
app_name = ssm.get_parameter(Name='APP_NAME', WithDecryption=True)['Parameter']['Value']
processing_job_role = ssm.get_parameter(Name='PROCESSING_JOB_ROLE', WithDecryption=True)['Parameter']['Value']
processing_job_data_input = ssm.get_parameter(Name='PROCESSING_JOB_DATA_INPUT', WithDecryption=True)['Parameter']['Value']
opensearch_domain_endpoint = ssm.get_parameter(Name='OPENSEARCH_DOMAIN_ENDPOINT', WithDecryption=True)['Parameter']['Value']
opensearch_index = ssm.get_parameter(Name='OPENSEARCH_INDEX', WithDecryption=True)['Parameter']['Value']
embedding_endpoint_name = ssm.get_parameter(Name='EMBEDDING_ENDPOINT_NAME', WithDecryption=True)['Parameter']['Value']

#  define the processing job parameters
base_job_name = f"{app_name}-embedding-processing-job"

#  Define the SageMaker processing job
instance_type = 'ml.m5.xlarge'
instance_count = 3
logger.info(f"image_uri={processing_job_image_uri}, instance_type={instance_type}, instance_count={instance_count}")

# Setup the ScriptProcessor 
processor = ScriptProcessor(role = processing_job_role,
                           base_job_name = base_job_name,
                            image_uri = processing_job_image_uri,
                            instance_type = instance_type,
                            instance_count = instance_count,
                            command = ['python3'],
                            sagemaker_session = sagemaker_session)

# setup input from S3, note the ShardedByS3Key, this ensures that 
# each instance gets a random and equal subset of the files in S3.

inputs = [ProcessingInput(source=processing_job_data_input,
                    destination='/opt/ml/processing/input_data',
                    s3_data_type='S3Prefix',
                    s3_data_distribution_type='ShardedByS3Key')]

#run the processing job
st = time.time()
processor.run(code="opensearch_ingestion.py",
              inputs=inputs,
              outputs=[],
              arguments=["--opensearch-cluster-domain", opensearch_domain_endpoint,
                         "--opensearch-index-name", opensearch_index,
                         "--region", region,
                         "--embeddings-model-endpoint-name", embedding_endpoint_name,
                         "--input-data-dir", "/opt/ml/processing/input_data",
                         "--process-count", "2"])
time_taken = time.time() - st
logger.info(f"processing job completed, total time taken={time_taken}s")
preprocessing_job_description = processor.jobs[-1].describe()
logger.info(preprocessing_job_description)