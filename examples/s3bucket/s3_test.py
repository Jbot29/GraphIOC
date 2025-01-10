
import GraphIOC 
from GraphIOC.aws.s3 import S3Bucket


def infra(gioc):

    test_bucket = S3Bucket(g_id="GraphIOC-Test-Bucket",bucket_name="grphi-test-bucket-1",region="us-east-2")
    print("WTF")
    GraphIOC.add_node(gioc,test_bucket)

    
