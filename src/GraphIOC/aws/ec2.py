#Graph IOC

import boto3

from pydantic import BaseModel
from typing import Optional,List
from botocore.exceptions import ClientError

"""

ec2 = session.client('ec2',region_name='us-east-1')
elb = session.client('elbv2',region_name='us-east-1')
ecs = session.client('ecs',region_name='us-east-1')
"""

class SecurityGroup(BaseModel):
    id: str
    desc: str
    vpc_id: str
    aws_id: Optional[str] = None

class ALB(BaseModel):
    id: str
    desc: str
    subnets: List[str]
    sg_id: str
    arn: Optional[str] = None


class TargetGroup(BaseModel):
    id: str
    desc: str
    vpc_id: str
    target_type: str
    arn: Optional[str] = None

class Listener(BaseModel):
    id: str
    desc: str
    lb_arn: str
    tg_arn: str


class ECSCluster(BaseModel):
    id: str
    desc: str

class ECSTaskDefinition(BaseModel):
    id: str
    desc: str
    
class ECSService(BaseModel):
    id: str
    desc: str

    
def check_security_group_exists(security_group_id):
    # Initialize a boto3 EC2 client
    ec2 = boto3.client('ec2')

    try:
        # Try to describe the security group by ID
        response = ec2.describe_security_groups(GroupIds=[security_group_id])
        # If successful, return True and details of the security group
        if response['SecurityGroups']:
            print(f"Security Group {security_group_id} exists.")
            return True, response['SecurityGroups'][0]
    except ClientError as e:
        # Catch the exception if the security group does not exist or another error occurs
        if 'InvalidGroup.NotFound' in str(e):
            print(f"Security Group {security_group_id} does not exist.")
        else:
            print(f"An error occurred: {e}")
    return False, None






def create_sg():
    response = ec2.create_security_group(
        GroupName=docbot_sg.id,
        Description=docbot_sg.desc,
        VpcId=docbot_sg.vpc_id
    )


    security_group_id = response['GroupId']


    print(security_group_id )


def sg_ingress(security_group_id):

    # Authorize inbound traffic (e.g., allow HTTP on port 80)
    response = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

    print(response)


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



def create_target_group(tg):
    # Step 3: Create a Target Group
    response = elb.create_target_group(
        Name=tg.id,
        Protocol='HTTP',
        Port=80,
        VpcId=tg.vpc_id,
        HealthCheckProtocol='HTTP',
        HealthCheckPort='80',
        HealthCheckPath='/',
        TargetType=tg.target_type
    )

    target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
    print(f"Target Group ARN: {target_group_arn}")

def create_listener(l):
    # Step 4: Create a Listener for the Load Balancer
    response = elb.create_listener(
        LoadBalancerArn=l.lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': l.tg_arn
            }
        ]
    )

    listener_arn = response['Listeners'][0]['ListenerArn']
    print(f"Listener ARN: {listener_arn}")


def create_ecs_cluster(s):


    response = ecs.create_cluster(
        clusterName=s.id
    )

    print(response['cluster']['clusterArn'])



def create_ecs_service(cluster,service,taskdef,targetgrp,subnets,sg,container_name):
    response = ecs.create_service(
        cluster=cluster.id,
        serviceName=service.id,
        taskDefinition=taskdef.id,
        loadBalancers=[
            {
                'targetGroupArn': targetgrp.arn,
                'containerName': container_name,
                'containerPort': 80
            }
        ],
        desiredCount=2,  # Number of tasks
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnets,
                'securityGroups': [
                    sg.aws_id
                ],
                'assignPublicIp': 'ENABLED'
            }
        }
    )

    print(f"Service ARN: {response['service']['serviceArn']}")    
