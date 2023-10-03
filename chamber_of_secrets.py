import boto3
import json
import os
import json
from botocore.exceptions import ClientError


def get_secret(secret_name):
    secrets = get_secrets_dict()
    try:
        return secrets[secret_name]
    except:
        return None


def get_secrets_dict():
    # Initialize the AWS Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-west-2"
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId="the_chamber_of_secrets"
        )
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        raise e
