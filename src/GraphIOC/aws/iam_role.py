import boto3
import time
from botocore.exceptions import ClientError
from pydantic import BaseModel
from typing import Optional,List

def role_exists(role_name):
    try:
        # Check if the role already exists
        role_response = iam_client.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists.")
        role_arn = role_response['Role']['Arn']
    except iam_client.exceptions.NoSuchEntityException:
        return False

    return True

def role_create(role_name,policy_document):
    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }    
    create_role_response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=str(assume_role_policy_document),
        Description='Role for Lambda execution',
    )
    role_arn = create_role_response['Role']['Arn']

    # Attach a basic execution policy to the role
    print(f"Attaching AWSLambdaBasicExecutionRole policy to {role_name}")
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )    
    pass

def role_get(role_name):
    role_response = iam_client.get_role(RoleName=role_name)
    print(f"Role '{role_name}' already exists.")
    role_arn = role_response['Role']['Arn']
    
    pass

class IAMRole(BaseModel):
    g_id: str
    name: str
    policy: str
    arn: str

    def exists(self,session):
        pass

    def create(self,session,G):
        pass

    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass
    

    
