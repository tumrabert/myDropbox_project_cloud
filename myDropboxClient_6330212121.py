import requests
import base64
from dotenv import load_dotenv
<<<<<<< HEAD
import hashlib


# Load environment variables from a .env file
load_dotenv()

API_GATEWAY = os.getenv("API_GATEWAY") + '/act5v2/api/v1'
def hash_password(password):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the password bytes
    sha256.update(password_bytes)
    # Get the hashed password in hexadecimal format
    hashed_password = sha256.hexdigest()
    return hashed_password


=======
import os

# Load environment variables from .env file
load_dotenv()
API_GATEWAY = os.getenv("API_GATEWAY")
PATH='/act5v2/api/v1'
HEADERS = {'Content-Type': 'application/json'}
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
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
<<<<<<< HEAD
    url = f"{API_GATEWAY}/{endpoint}"
=======
    url = f"{API_GATEWAY+PATH}/{endpoint}"
    print('REST->',url)
    print('data->',data)
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.request(method=method, url=url, headers=headers, json=data)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None, None
<<<<<<< HEAD

def put(file_name,owner):
=======
    
def put(file_name):
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
    """Uploads a file to the API."""
    file_path = f"./{file_name}"
    file_content = get_file_content_base64(file_path)

    if not file_content:
        return False

    data = {
<<<<<<< HEAD
        'owner': owner,
        'file_name': file_name,
        'file': file_content
=======
        "owner": "tumrabert",  
        "file_name": file_name,
        "file_object": file_content
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
    }

    status_code, _ = make_api_request('PUT', 'put', data)
    if status_code == 200:
        print("File uploaded successfully.")
        return True
    else:
        print("Error uploading file.")
        return False

<<<<<<< HEAD
def view(owner):
    """Lists files associated with the specified owner."""
=======
def view(owner="tumrabert"):
    # Assuming 'view' can be called with a GET request without parameters
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
    if not owner:
        print("Owner's name cannot be empty.")
        return False

    data = {'owner': owner}
    status_code, files = make_api_request('GET', 'view', data)
    if status_code == 200 and files:
<<<<<<< HEAD
        for file in files['files']:
            print(file)
        return True
=======
        print(files)
>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
    else:
        print("No files found for this owner.")
        return False

def get(file_name, owner):
    """Downloads a file from the API."""
    data = {'owner': owner, 'file_name': file_name}
    status_code, response_data = make_api_request('GET', 'get', data)

    if status_code == 200 and response_data:
        file_url = response_data.get('file_url')
        if file_url:
            print("Downloading file...")
            response = requests.get(file_url)
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully.")
            return True
        else:
            print("File not found.")
            return False
    else:
        print("Error fetching file.")
        return False
    
def createUser(user,password):
    print(f"Creating a new user => {user}") 
    hashed_pwd = hash_password(password)
    data = {'username': user, 'password': hashed_pwd}
    status_code, respond= make_api_request('POST', 'user_auth/register', data)
    if status_code == 200:
        print(f"User {user} created successfully.")
    else:
        print(respond)
        print(f"User {user} already exists.")
def login(user,password):
    hash_pw=hash_password(password)
    data = {'username':user,'password':hash_pw}
    status_code, response_data = make_api_request('POST', 'user_auth/login', data)
    if status_code == 200:
        print("Login successfully.")
        return True
    else:
        print("Login Failed.")
        print(response_data)
        return False
    
def check_user_exists(username):
    data = {'username': username}
    try:
        status_code, response = make_api_request('GET', 'user_auth/checkuser', data)
        if status_code == 200:
            return True, "User exists"
        elif status_code == 404:
            return False, "User does not exist"
        else:
            return False, f"Error: {response}"
    except Exception as e:
        return False, f"Error: {e}"

def share(owner,filename,userToShare):

    if(check_user_exists(userToShare)):
        data = {'owner': owner, 'filename': filename, 'shareTo': userToShare}
        status_code,response = make_api_request('POST', 'share', data)
        if status_code == 200:
            print(f"File {filename} shared with {userToShare} successfully.")
        else:
            print("Failed to shared file")
            print(response)
            return False
    else:
        print(f"{userToShare} is not Existed")
        return False
    return True

def check_download_permission(username, file_name, owner):
    """Checks if the user has permission to download the file."""
    data = {'owner': username}
    status_code, response = make_api_request('GET', 'view', data)
    if status_code == 200 and response:
        files = response.get('files', [])
        shared_files = response.get('sharefile', [])
        if files:
            for file in files:
                if file['Key'] == file_name and file['owner'] == owner:
                    return True
        if shared_files:
            for file in shared_files:
                if file['Key'] == file_name and file['owner'] == owner:
                    return True
    return False


'''def select_function(ip,username):
    global USER
    if(ip[0]=='put'):
        print("OK") if put(ip[1],username) else print("put error")
    elif(ip[0]=='view'):
        print("OK") if view(username) else print("view error")
    elif(ip[0]=='get'):
        if(check_download_permission(username, ip[1],ip[2])):
            print("OK") if get(ip[1],ip[2]) else print("get error")
        else:
            print("You do not have permission to download this file.")        
    elif(ip[0]=='newuser'):
        print("OK") if createUser(ip[1],ip[3]) else print("Create User Error")
    elif(ip[0]=='login'):
        if login(ip[1],ip[2]):
            USER=username
            print("OK") 
        else:
            USER=""
            print("Login user invalid username or password")
    elif(ip[0]=='share'):
        print("OK") if share(username,ip[1],ip[2]) else print("share error")
    else:
        print("Please input correct command")
        return'''
    
def main():
    print("Welcome to myDropbox Application")
    print("===================================")
    print("Available commands:")
    print("newuser username password password")
    print("login username password")
    print("put filename")
    print("get filename owner")
    print("share filename userToshare")
    print("view")
    print("logout")
    print("quit")
    print("===================================")
    username = None
    while True:
        print("MY USER",username)
        user_input = input(">> ").split()
        command = user_input[0]
        if command == 'quit':
            break

<<<<<<< HEAD
        if command not in ['newuser', 'login', 'put', 'get', 'view', 'logout', 'share']:
            print("Please input a correct command.")
            continue

        if command == 'logout':
            username = None
            print("You're Logged out.")
            continue

        if username:  # Already logged in
            allowed_commands = ['newuser', 'put', 'get', 'view', 'logout', 'share']
            if user_input[0] in allowed_commands:
                #select_function(user_input, USER)
                if(command=='put'):
                    print("OK") if put(user_input[1],username) else print("put error")
                elif(command=='view'):
                    print("OK") if view(username) else print("view error")
                elif(command=='get'):
                    if(check_download_permission(username, user_input[1],user_input[2])):
                        print("OK") if get(user_input[1],user_input[2]) else print("get error")
                    else:
                        print("You do not have permission to download this file.")        
                elif(command=='newuser'):
                    print("OK") if createUser(user_input[1],user_input[3]) else print("Create User Error")
                elif(command=='share'):
                    print("OK") if share(username,user_input[1],user_input[2]) else print("share error")
                else:
                    print("Please input correct command")
                    return
            else:
                print("You're not allowed to use this command1.")
        else:
            allowed_commands = ['newuser', 'login']
            if user_input[0] in allowed_commands:
                #select_function(user_input, USER)
                if(command=='newuser'):
                    print("OK") if createUser(user_input[1],user_input[3]) else print("Create User Error")
                elif(command=='login'):
                    if login(user_input[1],user_input[2]):
                        username=user_input[1]
                        print("OK") 
                    else:
                        print("Login user invalid username or password")
                else:
                    print("Please input correct command")
                    return
            else:
                print("You're not allowed to use this command2.")

if __name__ == "__main__":
    main()
=======
print("welcome to myDropbox Application")
print('''======================================================
Please input command (newuser username password password, login 
username password, put filename, get filename, view, or logout). 
If you want to quit the program just type quit.
======================================================''')
ip=input(">>").split()

while(ip[0]!='quit'):
    
    if(ip[0]not in ['newuser','login','put','get','view','logout']):
        continue
    select_function(ip)
    ip=input(">>").split()
print("======================================================")


>>>>>>> b9319fc4c25aa0d547c3579e5e179a0c88c59abe
