import boto3

from pydantic import BaseModel
from typing import Optional,List
from botocore.exceptions import ClientError

from ..models import BaseNode


class ALB(BaseNode):
    id: str
    desc: str
    subnets: List[str]
    sg_id: str
    arn: Optional[str] = None


def create_alb(alb):
    response = elb.create_load_balancer(
        Name=alb.id,
        Subnets=alb.subnets,
        SecurityGroups=[alb.sg_id],
        Scheme='internet-facing',
        Tags=[
        {
            'Key': 'Name',
            'Value': 'my-alb'
        }
        ],
        Type='application',
        IpAddressType='ipv4'
    )

    load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"ALB ARN: {load_balancer_arn}")


import boto3

def create_alb_for_lambda(
    load_balancer_name: str,
    subnets: list[str],
    security_groups: list[str],
    lambda_arn: str,
    vpc_id: str,
    region_name: str = "us-east-1"
):
    """
    Creates an internet-facing Application Load Balancer in the specified subnets,
    a target group of type 'lambda', and sets up a listener forwarding to the Lambda.

    :param load_balancer_name: Name of the ALB (must be unique within the region/account).
    :param subnets: List of subnet IDs for the ALB. Typically 2+ subnets in different AZs.
    :param security_groups: List of security group IDs for the ALB.
    :param lambda_arn: ARN of your Lambda function (e.g. "arn:aws:lambda:us-east-1:123456789012:function:MyLambda").
    :param vpc_id: The ID of the VPC where the ALB should be created.
    :param region_name: AWS region (e.g., "us-east-1").
    :return: Dictionary with information about the created resources.
    """

    # ---------------------------------------------
    # 1) Create the Load Balancer
    # ---------------------------------------------
    elbv2 = boto3.client("elbv2", region_name=region_name)

    print(f"Creating ALB: {load_balancer_name} ...")
    lb_response = elbv2.create_load_balancer(
        Name=load_balancer_name,
        Subnets=subnets,
        SecurityGroups=security_groups,
        Scheme="internet-facing",  # or 'internal' for private
        IpAddressType="ipv4",
        Type="application"
    )
    load_balancer_arn = lb_response["LoadBalancers"][0]["LoadBalancerArn"]
    print(f"Created ALB ARN: {load_balancer_arn}")

    # ---------------------------------------------
    # 2) Create Target Group of type 'lambda'
    # ---------------------------------------------
    target_group_name = f"{load_balancer_name}-tg-lambda"
    print(f"Creating Lambda Target Group: {target_group_name} ...")
    tg_response = elbv2.create_target_group(
        Name=target_group_name,
        TargetType="lambda",
        # For a Lambda target group, you still specify Protocol/Port,
        # but they won't be used in the same way as instance targets.
        Protocol="HTTP",
        Port=80,
        VpcId=vpc_id
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]
    print(f"Created Target Group ARN: {target_group_arn}")

    # ---------------------------------------------
    # 3) Register the Lambda as a target
    # ---------------------------------------------
    print("Registering Lambda function as target...")
    elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{"Id": lambda_arn}]
    )
    print("Lambda successfully registered with target group.")

    # ---------------------------------------------
    # 4) Create a Listener (HTTP on Port 80)
    # ---------------------------------------------
    print("Creating Listener on port 80 ...")
    listener_response = elbv2.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol="HTTP",
        Port=80,
        DefaultActions=[
            {
                "Type": "forward",
                "TargetGroupArn": target_group_arn
            }
        ]
    )
    listener_arn = listener_response["Listeners"][0]["ListenerArn"]
    print(f"Created Listener ARN: {listener_arn}")

    # ---------------------------------------------
    # 5) Add permission so ALB can invoke Lambda
    # ---------------------------------------------
    print("Adding permission to Lambda for ALB invocation ...")
    lambda_client = boto3.client("lambda", region_name=region_name)

    # We add a resource policy statement allowing 'elasticloadbalancing.amazonaws.com'
    # to invoke this Lambda, with the SourceArn = target group's ARN.
    statement_id = "AllowInvocationFromALB"
    function_name = lambda_arn  # can also be partial ARN or name, but full ARN is fine

    # If there's already a statement with the same ID, it fails. We'll handle gracefully:
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="elasticloadbalancing.amazonaws.com",
            SourceArn=target_group_arn
        )
        print("Successfully added permission to Lambda.")
    except lambda_client.exceptions.ResourceConflictException:
        print("Permission already exists on the Lambda function. Skipping.")

    return {
        "LoadBalancerArn": load_balancer_arn,
        "TargetGroupArn": target_group_arn,
        "ListenerArn": listener_arn
    }

# ---------------------------------------------------------
# Usage Example
# ---------------------------------------------------------

    # You'll need your own AWS credentials or a profile set up
    # Possibly: session = boto3.Session(profile_name="myProfile")

#    load_balancer_name = "my-lambda-alb"
#    subnets = ["subnet-abc123456", "subnet-def789012"]   # At least two subnets in different AZs
#    security_groups = ["sg-0123abcdef"]                  # Security group for the ALB
#    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:MyFastAPILambda"
#    vpc_id = "vpc-0123abc456def7890"

#    create_alb_for_lambda(
#        load_balancer_name=load_balancer_name,
#        subnets=subnets,
#        security_groups=security_groups,
#        lambda_arn=lambda_arn,
#        vpc_id=vpc_id,
#        region_name="us-east-1"
#    )
