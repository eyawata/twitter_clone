import os
from functools import lru_cache

import boto3


@lru_cache()
def get_dynamo_resource():
    return boto3.resource("dynamodb", region_name=os.getenv("ap-northeast-1"))


def get_table(table_name: str):
    """
    Returns a Table instance. Use in routers via Depends.
    """
    return get_dynamo_resource().Table(table_name)
