import boto3
import json
import os


'''
create dynamodb & s3 resource
'''
s3_client = boto3.client('s3')
dynamodb_client = boto3.resource('dynamodb')
dynamoTable = dynamodb_client.Table(os.environ['DYNAMODB_TABLE'])


def build_response(statuscode, body=None):
    response = {
        "statusCode": statuscode,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response