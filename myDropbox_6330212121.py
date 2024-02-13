import json
import boto3
import os
s3 = boto3.client('s3')
BUCKET_NAME = os.environ['s3_BUCKET_NAME']
def lambda_handler(event, context):
    
    http_method = event["httpMethod"]
    endpoint = event["path"]

    if http_method == "GET" and endpoint == "/act5v2/api/v1/get":
        body = json.loads(event["body"])
        filename = body.get("filename")
        return getMethod(filename)
    elif http_method == "PUT" and endpoint == "/act5v2/api/v1/put":
        body = json.loads(event["body"])
        filename = body.get("filename")
        file_object = body.get("file_object")
        return putMethod(filename, file_object)
    elif http_method == "GET" and endpoint == "/act5v2/api/v1/view":
        return viewMethod()
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Endpoint not found"})
        }

def getMethod(filename):
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_content = response['Body'].read().decode('utf-8')
        return {
            "statusCode": 200,
            "body": file_content
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }

def putMethod(filename, file_object):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=file_object)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "File uploaded successfully"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }

def viewMethod():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files_info = []
        for obj in response.get('Contents', []):
            file_info = {
                "filename": obj['Key'],
                "lastModifiedDate": obj['LastModified'].isoformat(),
                "size": obj['Size'],
                "owner": obj['Owner']['DisplayName']
            }
            files_info.append(file_info)
        return {
            "statusCode": 200,
            "body": json.dumps(files_info)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
