import boto3
import os 
from dotenv import dotenv_values


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
config = dotenv_values(dotenv_path)
session = boto3.Session(profile_name='dustin-dev2-admin', region_name='ap-southeast-2')
ssm = session.client('ssm')

def push_to_ssm(key,value):
    ssm.put_parameter(
        Name=key,
        Value=value,
        Type='String',
        Overwrite=True
    )

for key, value in config.items():
    print(key, value)
    push_to_ssm(key, value)

