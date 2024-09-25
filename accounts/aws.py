import os
import boto3
from dotenv import load_dotenv


def get_secret(prod=False):
    load_dotenv()

    secret_name = (
        os.environ.get("AWS_SECRET_NAME_PROD")
        if prod
        else os.environ.get("AWS_SECRET_NAME")
    )
    region_name = os.environ.get("AWS_REGION_NAME")

    # Create a Secrets Manager client
    client = boto3.client(
        service_name="secretsmanager",
        region_name=region_name,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        raise e

    return get_secret_value_response["SecretString"]
