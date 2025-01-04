
from GraphIOC.aws.route53 import HostedZone
from GraphIOC.aws.certificate import Certificate,CertificateHostedZoneEdge,get_dns_validation
from GraphIOC.aws.s3 import S3Bucket

BASE_MODEL_MAP = {
    "HostedZone": HostedZone,
    "Certificate": Certificate,
    "CertificateHostedZoneEdge": CertificateHostedZoneEdge,
    "S3Bucket": S3Bucket
}
