import os
import zipfile
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel,constr,Field
from typing import Optional,List
from ..models import BaseNode

from .types import AwsName
from .iam_role import IAMRolePolicyEdge

#TODO fix region


class IAMRolePolicyLambdaEdge(IAMRolePolicyEdge):
    policy_arn: str = "arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole"

class LambdaZipFile(BaseNode):
    g_id: str
    name: AwsName
    runtime: str
    handler:str 
    zip_file_path: str
    description: Optional[str] = Field("No description", description="A description of the lambda") 
    timeout: Optional[int] = 15
    memory_size: Optional[int] = 128
    publish: Optional[bool] = True
    
    def exists(self,session):
        if lambda_exists(session, self.name):
            return True
        return False


    def create(self,session,G):
        print("CREATE")
        role_edge = None
        
        incoming_edges = G.in_edges(self.g_id)
        for ie in incoming_edges:
            edge = G[ie[0]][ie[1]]
            edge_data = edge['data']
            if isinstance(edge_data,IAMRolePolicyLambdaEdge):
                role_edge = edge_data

        print(role_edge)
        print("2",role_edge.role_g_id)
        print(G.nodes[role_edge.role_g_id]['data'])
        iam_role = G.nodes[role_edge.role_g_id]['data']
            
        
        return lambda_create(session,self.name,self.runtime,iam_role.arn,self.handler,self.description,self.timeout,self.memory_size,self.publish,self.zip_file_path)

    def read(self, session,G):
        # cloned = self.copy(deep=True)
        response = lambda_read(session,self.name)
        if not response:
            return None
        

        current_config = LambdaZipFile(
            g_id=self.g_id,  # Or store separately if AWS doesn't have this
            name=self.name,  # The name won't change
            runtime=response.get('Runtime'),
            handler=response.get('Handler'),
            zip_file_path=self.zip_file_path,  # Not tracked by AWS
            description=response.get('Description'),
            timeout=response.get('Timeout'),
            memory_size=response.get('MemorySize'),
            publish=self.publish  # AWS doesn't store this boolean
        )

        return current_config

        
    def update(self,session,G):
        return lambda_update(session,self)

    def delete(self,session,G):
        pass

    def diff(self,session,G,diff_object):
        return True



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

        

def lambda_create(session,function_name,runtime,role_arn,handler,description,timeout,memory_size,publish,zip_file_name):
    lambda_client = session.client('lambda',region_name='us-east-1')
    # Read zip file bytes
    with open(zip_file_name, 'rb') as f:
        zip_bytes = f.read()

    print(len(zip_bytes))
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
        MemorySize=memory_size,
        Publish=publish
    )
    
"""

def update_lambda_code(lambda_client, function_name, zip_file_path):
    try:
        # Open the new zip file to update the Lambda function
        with open(zip_file_path, 'rb') as zip_file:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file.read()  # Upload the new zip file content
            )
        
        # Print the response from Lambda after updating the function
        print("Lambda function updated successfully!")
        print("Response:", response)

    except Exception as e:
        print("Error updating Lambda function:", e)

# Initialize the Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Specify the Lambda function name and path to the new zip file
function_name = 'my-lambda-function'
zip_file_path = 'lambda_code.zip'

# Call the update function
update_lambda_code(lambda_client, function_name, zip_file_path)


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


import boto3
from typing import Optional

def lambda_read(session,func_name):
    lambda_client = session.client('lambda',region_name='us-east-1')


    try:
        # Get the current AWS configuration for this Lambda function
        response = lambda_client.get_function_configuration(
            FunctionName=func_name
        )

        # Build a new model using AWS's current settings; 
        # For fields that AWS doesn't store (zip_file_path, publish), 
        # we keep the local model's values.


        return response

    except lambda_client.exceptions.ResourceNotFoundException:
        # If AWS cannot find the Lambda by that name, return None
        return None
    except Exception as e:
        # In a real-world scenario, handle or log the exception
        print(f"An error occurred: {e}")
        return None




def lambda_update(
    session,
        lambda_config,
        region_name = "us-east-1"
):
    lambda_client = session.client('lambda',region_name=region_name)
    """
    Checks an existing Lambda function against the provided LambdaZipFile config.
    If settings differ, update them. Also re-uploads code from 'zip_file_path'.
    
    :param session: A boto3 Session with credentials.
    :param lambda_config: The desired Lambda configuration (name, runtime, handler, etc.).
    :param region_name: The AWS region in which the Lambda resides.
    :return: A dict describing actions taken. 
             For example: {"updated_config": True, "updated_code": True}
    """

    function_name = lambda_config.name

    # Prepare a response dictionary describing what (if anything) we changed
    result = {"updated_config": False, "updated_code": False, "error": None}
    
    # 1. Check if the function exists and retrieve current configuration
    try:
        current = lambda_client.get_function_configuration(FunctionName=function_name)
    except lambda_client.exceptions.ResourceNotFoundException:
        result["error"] = f"Lambda function '{function_name}' does not exist."
        return result
    except ClientError as e:
        result["error"] = f"Unexpected error accessing Lambda: {e}"
        return result

    # 2. Compare AWS config to local config. We'll build an update dict dynamically.
    config_updates = {}
    
    if current.get("Runtime") != lambda_config.runtime:
        config_updates["Runtime"] = lambda_config.runtime

    if current.get("Handler") != lambda_config.handler:
        config_updates["Handler"] = lambda_config.handler

    if current.get("Description") != lambda_config.description:
        config_updates["Description"] = lambda_config.description

    if current.get("Timeout") != lambda_config.timeout:
        config_updates["Timeout"] = lambda_config.timeout

    if current.get("MemorySize") != lambda_config.memory_size:
        config_updates["MemorySize"] = lambda_config.memory_size

    # 3. Update function configuration if needed
    if config_updates:
        try:
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                **config_updates
            )
            result["updated_config"] = True
        except ClientError as e:
            result["error"] = f"Failed to update Lambda config: {e}"
            return result

    # 4. Re-upload code if the zip is different or if you always want to re-deploy code
    #    (Here, we'll always re-upload to ensure code is in sync with local zip).
    zip_path = lambda_config.zip_file_path
    if not os.path.isfile(zip_path):
        result["error"] = f"Zip file does not exist: {zip_path}"
        return result

    try:
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()
        
        if len(zip_bytes) == 0:
            result["error"] = f"Zip file is empty: {zip_path}"
            return result

        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes,
            Publish=lambda_config.publish
        )
        result["updated_code"] = True

    except ClientError as e:
        result["error"] = f"Failed to update Lambda code: {e}"

    return result
