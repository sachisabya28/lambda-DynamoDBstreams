from auth.user import s3_client, dynamoTable, build_response
import base64
import os

BUCKET_NAME = os.getenv('BUCKET_NAME')


def fileupload(event, context):
    # print('fileuploadvent', event)
    file_name = event['headers']['filename']
    file_content = event['body']
    try:
        s3_response = s3_client.put_object(Bucket=BUCKET_NAME,
                                           Key=file_name,
                                           Body=file_content)
        # print('S3 Response: {}'.format(s3_response))
        s3_response['body'] = 'Your file has been uploaded'
        return build_response(200, s3_response['body'])
    except Exception as e:
        raise IOError(e)


def getupload(event, context):
    # print('getupload', event)
    file_name = event["queryStringParameters"]["file"]
    fileObj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
    file_content = fileObj['Body'].read().decode('utf-8')
    return {"body": file_content}


def upload_dynamo(event, context):
    if event:
        # print("Event: ", event)
        file_obj = event["Records"][0]
        filename = str(file_obj['s3']['object']['key'])
        # print("Filename: ", filename)
        dynamoTable.put_item(Item = {
            'filename': str(filename)
        })
        
