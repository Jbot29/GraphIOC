import os
import zipfile
import boto3

# ---------------------------------------
# 1. (Optional) Create or retrieve an IAM role for Lambda to assume
# ---------------------------------------
iam_client = boto3.client('iam')
role_name = 'MyLambdaExecutionRole'

# Try to get or create the role
try:
    # Check if the role already exists
    role_response = iam_client.get_role(RoleName=role_name)
    print(f"Role '{role_name}' already exists.")
    role_arn = role_response['Role']['Arn']
except iam_client.exceptions.NoSuchEntityException:
    # If role doesn't exist, create a new one
    print(f"Creating new IAM role: {role_name}")
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
lambda_client = boto3.client('lambda')

function_name = 'MyFirstLambdaFunction'
runtime = 'python3.9'
handler = 'lambda_function.lambda_handler'  # fileName.functionName

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
    Description='My first Lambda function created via boto3',
    Timeout=15,       # Timeout in seconds
    MemorySize=128,   # MB
    Publish=True      # Whether to publish a new version
)

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
