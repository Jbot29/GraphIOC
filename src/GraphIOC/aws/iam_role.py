import boto3
import time
import json
from botocore.exceptions import ClientError
from pydantic import BaseModel,constr
from typing import Optional,List

class IAMRole(BaseModel):
    g_id: str
    name: constr(pattern=r'^[A-Za-z0-9+=,.@_-]+$')
    policy: dict
    arn: Optional[str] = None    


    def exists(self,session):
        print(f"{self.__class__.__name__}: Exists {self}")
        if role_exists(session,self.name):
            return True
        return False 

    def create(self,session,G):
        print(f"{self.__class__.__name__}: Create {self}")
        return role_create(session,self.name,self.policy)


    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass
    

    
def role_exists(session,role_name):
    iam_client = session.client('iam')
    try:
        # Check if the role already exists
        role_response = iam_client.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists.")
        role_arn = role_response['Role']['Arn']
    except iam_client.exceptions.NoSuchEntityException:
        return False

    return True

def role_create(session,role_name,policy_document):
    iam_client = session.client('iam')

    create_role_response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(policy_document),
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


    
