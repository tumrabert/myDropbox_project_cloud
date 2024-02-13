import boto3
import json
import requests
import base64
import os
from dotenv import load_dotenv
API_GATEWAY = os.getenv("API_GATEWAY") + '/act5v2/api/v1'
def get_file_content_base64(file_path):
    """Reads a file and returns its base64 encoded content."""
    try:
        with open(file_path, 'rb') as file:
            file_content_binary = file.read()
            return base64.b64encode(file_content_binary).decode('utf-8')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
def make_api_request(method, endpoint, data=None):
    """Makes an API request and returns the response status code and content."""
    url = f"{GATEWAY}/{endpoint}"
    print(url)
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None, None

def put(file_name):
    """Uploads a file to the API."""
    file_path = f"./{file_name}"
    file_content = get_file_content_base64(file_path)

    if not file_content:
        return

    data = {
        'owner': "p",  
        'file_name': file_name,
        'file': file_content
    }

    status_code, _ = make_api_request('PUT', 'put', data)
    if status_code == 200:
        print("File uploaded successfully.")

def view(owner="p"):
    # Assuming 'view' can be called with a GET request without parameters
    if not owner:
        print("Owner's name cannot be empty.")
        return
    data = {'owner': owner}
    status_code, files = make_api_request('GET', 'view', data)
    print(files,type(files))
    if status_code == 200 and files:
        for file in files['files']:
            print(file)
    else:
        print("No files found for this owner.")

def get(file_name, owner):
    """Downloads a file from the API."""
    data = {'owner': owner, 'file_name': file_name}
    response = make_api_request('GET', 'get', data)

    if not response:
        return
    json_data = response[1]

    # Access the 'file_url' key in the JSON data
    file_url = json_data.get('file_url')
    if file_url:
        print("Downloading file...")
        response = requests.get(file_url)
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("File not found.")

def select_function(ip):
    if(ip[0]=='put'):
        put(ip[1])
    elif(ip[0]=='view'):
        view()
    elif(ip[0]=='get'):
        get(ip[1],ip[2])
    else:
        print("Please input correct command")
        return
    print("OK")
        

print("welcome to myDropbox Application")
print('''======================================================
Please input command (newuser username password password, login 
username password, put filename, get filename, view, or logout). 
If you want to quit the program just type quit.
======================================================''')
ip=input().split()

while(ip[0]!='quit'):
    ip=input().split()
    select_function(ip)
print("======================================================")

