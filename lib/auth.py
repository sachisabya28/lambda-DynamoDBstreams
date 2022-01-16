import boto3
import os
import json
import datetime
from boto3.dynamodb.conditions import Key, Attr

dynamodb_client = boto3.resource('dynamodb')
dynamoTable = dynamodb_client.Table(os.environ['DYNAMODB_TABLE'])
dynamobatteryTable = dynamodb_client.Table(os.environ['DYNAMODB_BATTERY_TABLE'])


def _build_response(statuscode, body=None):
    '''
    Build custom response
    '''
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


def handledynamostream(event, context):
    '''
    lambda-handler associated to dynamodb stream
    whenever INSERT and MODIFY takes place in devicedata
    data is then inserted into batterydata
    '''
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            handle_insert(record)
        elif record['eventName'] == 'MODIFY':
            handle_modify(record)
    return

def handle_insert(record):
    '''
    lambda-handler when INSERT takes place in devicedata
    '''
    newImage = record['dynamodb']['NewImage']
    serial_number = newImage['serial_number']['S']
    created_date = newImage['created_date']['S']
    battery_state = newImage['battery_state']['S']
    payload = {
            'serial_number': serial_number,
            'battery_state': battery_state,
            'created_time': created_date
        }
    dynamo_response = dynamoTable.put_item(Item=payload)
    return



def handle_modify(record):
    '''
    lambda-handler when MODIFY takes place in devicedata
    '''
    oldImage = record['dynamodb']['OldImage']
    newImage = record['dynamodb']['NewImage']
    oldSerial = oldImage['serial_number']['S']
    newSerial = newImage['serial_number']['S']
    oldCreateddate = oldImage['created_date']['S']
    newCreateddate = newImage['created_date']['S']
    oldBatteryState = oldImage['battery_state']['S']
    newBatteryState = newImage['battery_state']['S']
    
    response = dynamobatteryTable.update_item(
        Key={
            'serial_number': oldSerial,
            'created_date': oldCreateddate
        },
        UpdateExpression="set serial_number=:r, battery_state=:p, created_time=:a",
        ExpressionAttributeValues={
            ':r': newSerial,
            ':p': newBatteryState,
            ':a': newCreateddate
        },
        ReturnValues="UPDATED_NEW"
    )
    return

def deviceupload(event, context):
    '''
    stores device info to dynamodb devicedata
    '''
    if event:
        device_data = json.loads(event['body'])['data']
    try:
        if 'serial_number' not in device_data:
            return _build_response(422, body={
                'message': "Validation Failed, empty serial_number"
                })
        if 'battery_state' not in device_data:
            return _build_response(422, body={
                'message': "Validation Failed, empty battery_state"
                })
        payload = {
            'serial_number': device_data['serial_number'],
            'battery_state': device_data['battery_state'],
            'created_time': datetime.datetime.now().isoformat()
        }
        dynamo_response = dynamoTable.put_item(Item=payload)
        if dynamo_response:
            body = {
                'response': 'battery state saved',
            }
            return _build_response(200, body)
    except Exception as e:
        raise IOError(e)


def getdevicestate(event, context):
    '''
    get all the device and current battery_state
    '''
    device_data = json.loads(event['body'])['data']
    if 'serial_number' not in device_data:
        return _build_response(422, body={
            'message': "Validation Failed, empty serial_number"
            })
    serial_number = device_data['serial_number']
    response = dynamobatteryTable.get_item(Key={'serial_number': serial_number})
    if 'Item' in response:
        return response['Item']
    return 'No data found'


def alldevicestate(event, context):
    '''
    get all the device level data from DB
    '''
    response = dynamoTable.scan()
    Items = response['Items']
    body = {
            'data': Items
        }
    return _build_response(200, body)

