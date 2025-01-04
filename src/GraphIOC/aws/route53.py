import boto3

from pydantic import BaseModel
from typing import Optional,List
from botocore.exceptions import ClientError




import boto3
from botocore.exceptions import ClientError

class HostedZone(BaseModel):
    g_id: str
    zone_id: str
    domain_name: str

    def exists(self,session):
        #print(f"{self.__class__.__name__}: Check {self}")

        return check_hosted_zone_exists(session,self.domain_name)
    
    @classmethod
    def read(cls,session,g_id,domain_name):

        exist,zone_id = check_hosted_zone_exists(session,domain_name)

        if not exist:
            return False
        
        return HostedZone(g_id=g_id,zone_id=zone_id,domain_name=domain_name)
    


def check_hosted_zone_exists(session,domain_name):
    # Initialize the Route 53 client
    route53 = session.client('route53')
    
    try:
        # List all hosted zones and search for the domain name
        response = route53.list_hosted_zones()
        
        # Check each hosted zone's name against the provided domain name
        for zone in response['HostedZones']:
            # Hosted zone names in Route 53 end with a dot, so we add it to match
            if zone['Name'] == domain_name.rstrip('.') + '.':
                print(f"Hosted zone found: {zone['Id']}")
                return True, zone['Id']
                
        print("Hosted zone not found.")
        return False, None

    except ClientError as e:
        print(f"An error occurred: {e}")
        return False, None

