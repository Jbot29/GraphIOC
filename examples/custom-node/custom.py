


import boto3

# Initialize S3 client
s3 = boto3.client('s3')

# Define bucket name (must be globally unique)
bucket_name = 'my-unique-bucket-name-123456'

# Create the S3 bucket
s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}  # Adjust region as needed
)

# Define lifecycle configuration to delete objects after 365 days
lifecycle_configuration = {
    'Rules': [
        {
            'ID': 'Delete objects after one year',
            'Filter': {'Prefix': ''},
            'Status': 'Enabled',
            'Expiration': {'Days': 365}
        }
    ]
}

# Apply the lifecycle configuration to the bucket
s3.put_bucket_lifecycle_configuration(
    Bucket=bucket_name,
    LifecycleConfiguration=lifecycle_configuration
)

print(f"Bucket '{bucket_name}' created with a lifecycle rule to delete objects after one year.")
