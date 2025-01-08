
from GraphIOC.aws.route53 import HostedZone
from GraphIOC.aws.certificate import Certificate,CertificateHostedZoneEdge,get_dns_validation
from GraphIOC.aws.s3 import S3Bucket
from GraphIOC.aws.iam_role import IAMRole

from GraphIOC.aws.lambda_func import LambdaZipFile

BASE_MODEL_MAP = {
    "HostedZone": HostedZone,
    "Certificate": Certificate,
    "CertificateHostedZoneEdge": CertificateHostedZoneEdge,
    "S3Bucket": S3Bucket,
    "IAMRole": IAMRole,
    "LambdaZipFile": LambdaZipFile
}
