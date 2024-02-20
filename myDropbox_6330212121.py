import boto3
import json
import base64
import os
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key
BASE_PATH = '/act5v2/api/v1'
GET_PATH = f'{BASE_PATH}/get'
PUT_PATH = f'{BASE_PATH}/put'
VIEW_PATH = f'{BASE_PATH}/view'
CHECKUSER_PATH = f'{BASE_PATH}/user_auth/checkuser'
LOGIN_PATH = f'{BASE_PATH}/user_auth/login'
REGISTER_PATH = f'{BASE_PATH}/user_auth/register'
SHARE_PATH =f'{BASE_PATH}/share'
BUCKET_NAME = os.getenv('s3_BUCKET_NAME')
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
def lambda_handler(event, context):
    """Handles API requests for file operations."""
    try:
        path = event['path']
        body = json.loads(event["body"])

        if path == PUT_PATH:
            return _handle_put_request(body)
        elif path == GET_PATH:
            return _handle_get_request(body)
        elif path == VIEW_PATH:
            return _handle_view_request(body)
        elif path == CHECKUSER_PATH:
            return _handle_chkuser_request(body)
        elif path == REGISTER_PATH:
            return _handle_register_request(body)
        elif path == LOGIN_PATH:
            return _handle_login_request(body)
        elif path == SHARE_PATH:
            return _handle_share_request(body)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid path'})
            }
    except Exception as e:
        print(f"Error handling lambda request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def _get_object_key(owner, file_name):
    """Constructs the object key for a file based on owner and name."""
    return f"{owner}/{file_name}"

def list_files_for_owner(owner):
    
    files = []
    prefix = f"{owner}/"  # Assuming folder names are based on owners
    
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    for obj in response.get('Contents', []):
        dateTime = obj['LastModified']
        stringTime = dateTime.strftime('%Y-%m-%d %H:%M:%S')
        files.append({
            "Key":obj['Key'].split('/')[-1], 
            "Size": obj['Size'], 
            "LastModified": stringTime,
            "owner": owner
        })
    return files[1:]


def get_file_url(owner, file_name):
    """Generates a presigned URL for downloading a file."""
    files = list_files_for_owner(owner)
    file_key = _get_object_key(owner, file_name)
    
    if file_name not in files:
        return None
    file_key = f'{owner}/{file_name}'
    try:
        file_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': file_key}, ExpiresIn=3600)
        return file_url
    except Exception as e:
        print(f"Error generating URL for {file_key}: {e}")
        return None


def create_folder(folder_path):
    """Creates a folder in the bucket, ignoring errors if it already exists."""
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=folder_path)
    except Exception as e:
        print(f"Error creating folder {folder_path}: {e}")


def upload_file_to_s3(file_content, file_key):
    """Uploads a file to S3 with the specified key."""
    try:
        s3.put_object(Body=file_content, Bucket=BUCKET_NAME, Key=file_key)
    except Exception as e:
        print(f"Error uploading file {file_key}: {e}")





def _handle_put_request(body):
    """Handles PUT requests for uploading files."""
    try:
        owner = body.get('owner')
        file_name = body.get('file_name')
        file = body.get('file')

        if not all([owner, file_name, file]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        folder_path = _get_object_key(owner, '')
        create_folder(folder_path)

        file_content = base64.b64decode(file)
        file_key = _get_object_key(owner, file_name)
        upload_file_to_s3(file_content, file_key)

        return {
            'statusCode': 200,
            'body': json.dumps({'post': 'OK'})
        }
    except Exception as e:
        print(f"Error handling PUT request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


def _handle_get_request(body):
    """Handles GET requests for download file URLs."""
    try:
        file_name = body.get('file_name')
        owner = body.get('owner')

        if not all([file_name, owner]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        file_url = get_file_url(owner, file_name)
        if file_url:
            return {
                'statusCode': 200,
                'body': json.dumps({'file_url': file_url})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'File not found'})
            }
    except Exception as e:
        print(f"Error handling GET request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


def _handle_view_request(body):
    """Handles VIEW requests for listing files for an owner."""
    try:
        owner = body.get('owner')

        if not owner:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing owner field'})
            }

        files = list_files_for_owner(owner)
        sharefile = list_files_shared_with_user(owner)
        file_lists = convert_sharefile_to_list_files(sharefile)
        return {
            'statusCode': 200,
            'body': json.dumps({'files': files, 'sharefile': file_lists})
        }
    except Exception as e:
        print(f"Error handling VIEW request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    
def _handle_chkuser_request(body):
    """Handles VIEW requests for listing files for an owner."""
    try:
        username = body.get('username')

        if not username:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing username field'})
            }
        # Query dynamodb table to check if the username exists
        response = dynamodb.get_item(
            TableName='userTable',
            Key={
                'username': {'S': username}
            }
        )
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'{username} found in table'})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'{username} not found in table'})
            }
    except Exception as e:
        print(f"Error handling VIEW request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    
def _handle_register_request(body):
    """Handles REGISTER requests for creating a new user."""
    try:
        username = body.get('username')
        password = body.get('password')
        if not all([username, password]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        if (register_user(username, password)):
            return {
                'statusCode': 200,
                'body': json.dumps({'register': "OK"})
            }
        else:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'User already exists'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error handling REGISTER request'})
        }
    
def register_user(username, password):
    """Registers a new user in the database."""
    dynamo = boto3.resource('dynamodb')
    try:
        table = dynamo.Table('userTable')
        response = table.put_item(
        Item={
            'username': username,
            'password': password
        },
        ConditionExpression='attribute_not_exists(username)'
    )
        return True
    except Exception as e:
        return False 


def _handle_login_request(body):
    """Handles LOGIN requests for logging in a user."""
    try:
        username = body.get('username')
        password = body.get('password')
        
        if not all([username, password]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Implement login and session management
        response = login_user(username, password)
        if response:
            return {
                'statusCode': 200,
                'body': json.dumps({'login': 'OK'})
            }
        else:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }
    except Exception as e:
        print(f"Error handling LOGIN request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error handling LOGIN request'})
        }

def login_user(username, password):
  
    # Instantiate a table resource object
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('userTable')
    
    # Get the user from the database
    response = table.get_item(Key={'username': username})

    # Check if user exists and password matches
    if 'Item' in response:
        user = response['Item']
        if user['password'] == password:
            print("Login successful")
            return True
        else:
            print("Incorrect password")
            return False
    else:
        print("User does not exist")
        return False
def _handle_share_request(body):
    """Handles SHARE requests for sharing a file with another user."""
    try:
        owner = body.get('owner')
        filename = body.get('filename')
        shareTo = body.get('shareTo')

        if not all([owner, filename, shareTo]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Implement sharing logic
        if (owner == shareTo):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Cannot share with yourself'})
            }
        try:
            if sharefile(owner, filename, shareTo):
                return {
                    'statusCode': 200,
                    'body': json.dumps({'share': 'OK'})
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Owner user does not exist'})
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error sharing file {e}'})
            }
    except Exception as e:
        print(f"Error handling SHARE request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error handling SHARE request'})
        }
def sharefile(owner, filename, shareTo):
    share_id = str(uuid.uuid4())
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('shareTable')
    usertable = dynamo.Table('userTable') #userTable
    response = usertable.get_item(Key={'username': shareTo})
    if 'Item' not in response:
        return False
    try:
        response = table.put_item(
        Item={
            'shareId': share_id,
            'shareFrom': owner,
            'filename': filename,
            'shareTo': shareTo
        },
     )
        return True
    except Exception as e:
        return False

def list_files_shared_with_user(username):
    dynamo = boto3.resource('dynamodb')
    files = []
    table = dynamo.Table('shareTable')
    response = table.scan(
        FilterExpression=Key('shareTo').eq(username)
    )
    for item in response['Items']:
        files.append(item)
    return files

def convert_sharefile_to_list_files(sharefile):
    s3 = boto3.client('s3')
    file_list=[]
    for data in sharefile:
        file_owner = data['shareFrom']
        filename = data['filename']
        content = s3.head_object(Bucket = BUCKET_NAME, Key = file_owner + "/" + filename)
        file_size = content["ContentLength"]
        last_modified = content["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
        file_list.append({
            "Key": filename,
            "Size": file_size,
            "LastModified": last_modified,
            "owner": file_owner
        })
    return file_list