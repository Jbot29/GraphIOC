import os
import zipfile
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel,constr
from typing import Optional,List


from .types import AwsName

#TODO fix region

class LambdaZipFile(BaseModel):
    g_id: str
    name: AwsName
    runtime: str # = 'python3.9'
    handler:str # = 'lambda_function.lambda_handler'  # fileName.functionName
    zip_file_path: str
    role_g_id: str
    description: Optional[str] = Field("No description", description="A description of the lambda") 
    timeout: Optional[int] = 15
    memory_size: Optional[int] = 128
    publish: Optional[bool] = True
    
    def exists(self,session):
        if lambda_exists(session, self.name):
            return True
        return False


    def create(self,session,G):
        lambda_create(session,self.function_name,self.runtime,self.role_arn,self.handler,self.description,self.timeout,self.memory_size,self.publish):
        pass

    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass


def lambda_exists(session, function_name):
    lambda_client = session.client('lambda',region_name='us-east-1')
    try:
        # Attempt to retrieve the Lambda function configuration
        response = lambda_client.get_function(FunctionName=function_name)
        return True  # Function exists
    except ClientError as e:
        # Check for the 'ResourceNotFoundException'
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False  # Function doesn't exist
        else:
            raise  # Reraise the exception if it's not a 'ResourceNotFoundException'

        

def lambda_create(session,function_name,runtime,role_arn,handler,description,timeout,memory_size,publish):
    lambda_client = session.client('lambda',region_name='us-east-1')
    # Read zip file bytes
    with open(zip_file_name, 'rb') as f:
        zip_bytes = f.read()

    print(f"Creating Lambda function '{function_name}'...")
    create_fn_response = lambda_client.create_function(
            FunctionName=function_name,
        Runtime=runtime,
        Role=role_arn,  # The ARN of the IAM role
        Handler=handler,
        Code={
            'ZipFile': zip_bytes
        },
        Description=description,
        Timeout=timeout,
        MemorySize=memory_size
        Publish=publish
    )
    
"""
# ---------------------------------------
# 2. Zip your Lambda function code
# ---------------------------------------
# Suppose you have a file named 'lambda_function.py' in the current directory
lambda_file = 'lambda_function.py'
zip_file_name = 'function.zip'

print(f"Zipping code from {lambda_file} into {zip_file_name}...")
with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(lambda_file)

# ---------------------------------------
# 3. Create the Lambda function
# ---------------------------------------





print("Lambda function created successfully!")
print(f"Function ARN: {create_fn_response['FunctionArn']}")


lambda_client.update_function_code(
    FunctionName='MyFirstLambdaFunction',
    ZipFile=zip_bytes
)


lambda_client.update_function_configuration(
    FunctionName='MyFirstLambdaFunction',
    MemorySize=256,
    Environment={
        'Variables': {
            'LOG_LEVEL': 'DEBUG'
        }
    }
)

Environment={
    'Variables': {
        'MY_VAR': 'my_value'
    }
}


lambda_client.delete_function(FunctionName='MyFirstLambdaFunction')
"""
