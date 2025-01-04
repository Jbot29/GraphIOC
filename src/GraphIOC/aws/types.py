from pydantic import BaseModel,constr
from typing import NewType

# Define a custom type for the role name
AwsName = NewType('RoleName', constr(pattern=r'^[A-Za-z0-9+=,.@_-]+$'))
