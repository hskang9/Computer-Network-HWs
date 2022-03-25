from socket import *
from os import listdir, mkdir, getcwd, remove
from os.path import isfile, join, normpath, join
import re
from time import time

"""
file related functions
"""

def get_file_list(path):
    return listdir(path)

def make_personal_directory(username):
    try:
        # make a dir inside files/ directory
        curr_dir = getcwd()
        result = join(curr_dir, f"{username}")
        print(result)
        mkdir(result, 0o666)
    except FileExistsError:
        print("user directory already exists, moving on")

def save_cookie(user):
    with open(f"cookies/{user}", "wb") as file:
        timestamp = f"{time()}"
        file.write(timestamp.encode())

def delete_file(user, file):
    remove(f"{user}/{file}")

"""
http related functions
"""

def get_post_data(conn):
    data = b""
    while True:
        chunk = conn.recv(1024)
        if len(chunk) < 1024:
            return data + chunk
        else:
            data += chunk

def send_http_response(socket, filename):
    try:
        htmlFS = open('html' + filename)
        content = htmlFS.read()
        htmlFS.close()
        response = 'HTTP/1.0 200 Ok\n\n' + content
        socket.sendall(response.encode())
    except IOError:
        print("html file does not exist on:", filename)

def send_403(socket):
    response = 'HTTP/1.0 403 Forbidden\n' + '<h1>Forbidden</h1>'
    socket.sendall(response.encode())


def send_404(socket):
    response = 'HTTP/1.0 404 Not Found\n' + '<h1>Not Found</h1>'
    socket.sendall(response.encode())

def send_http_response_html(socket, html):
    response = 'HTTP/1.0 200 Ok\n\n' + html
    socket.sendall(response.encode())

def save_user_uploaded_file(packet, user):
    name = re.compile(b'name="submitted_file"; filename="(.+)"').search(packet).group(1)
    cut_front = re.compile(b"WebKitFormBoundary((\n|.)*)Content-Type.+\n.+?\n((\n|.)*)([\-]+WebKitFormBoundary)?").search(packet).group(3)
    # remove trailing boundary
    data = re.compile(b'(.*)(?=\\r\\n------)').search(cut_front).group(1)
    
    with open(f"{user}/{name.decode()}", "wb") as file:
        file.write(data)

def check_cookie(user):
    cookieFS = open('cookies' + f'/{user}')
    content = cookieFS.read()
    cookieFS.close()
    diff = (time() - float(content))
    return diff <= 120

"""
socket related functions(handler)
"""

def init_socket():
    serverPort = 10090
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
    server_socket.bind(('',serverPort))
    server_socket.listen(1)
    print('The server is ready to receive')
    return server_socket

def process_storage(packet, login_cache, connectionSocket):
    user = re.compile(b'(?<=name="id"\\r\\n\\r\\n)(.*?)(?=\\r\\n------)').search(packet)
    if user != None: 
        login_cache = process_login(packet, connectionSocket)
    else:
        print("upload request from /storage, change to upload")
        login_cache = process_upload(packet, login_cache, connectionSocket)
    return login_cache

def process_login(packet, connectionSocket):
    # get username and password
    user = re.compile(b'(?<=name="id"\\r\\n\\r\\n)(.*?)(?=\\r\\n------)').search(packet).group(1).decode()
    pw = re.compile(b'(?<=name="pw"\\r\\n\\r\\n)(.*?)(?=\\r\\n------)').search(packet).group(1).decode()
    # Make personal storage
    make_personal_directory(user)
    # Save Cookie 
    save_cookie(user)
     # Edit storage.html
    html = edit_user_storage_html(user)
    send_http_response_html(connectionSocket, html)
    return user

def process_upload(packet, login_cache, connectionSocket):
    # get user data
    save_user_uploaded_file(packet, login_cache)
    # Edit storage.html
    html = edit_user_storage_html(login_cache)
    send_http_response_html(connectionSocket, html)
    return login_cache   

def run_socket_connection(server_socket):
    # recently logged in user
    login_cache = ""
    while True:
        connectionSocket, addr = server_socket.accept()
        print('Accepted')
        request = connectionSocket.recv(1024).decode()
        print(request)
        headers = request.split('\n')
        #print(headers[0]) # <CODE(GET/PUT/POST/DELETE)> <URL> <HTTP Connection version>
        #print(headers[2]) # Connection: (keep-alive or smth)
        method =  headers[0].split()[0]
        url = headers[0].split()[1]
    
        # Build router
        # Assignment says it does not care url so just put file names and let it show the content from html file
        if method == "GET":
            # Exceptions on user customized page
            if url == '/storage':
                # check cookie
                if check_cookie(login_cache):
                     html = edit_user_storage_html(login_cache)
                     send_http_response_html(connectionSocket, html)
                else:
                    send_403(connectionSocket)
                
            elif url == "/":
                send_http_response(connectionSocket, '/index.html')
            
            elif url.startswith('/delete'):
                url_input = url.split('/')
                user, file = url_input[2], url_input[3] 
                # delete file 
                delete_file(user, file)
                html = edit_user_storage_html(login_cache)
                send_http_response_html(connectionSocket, html)

            # cookie management
            elif url == '/cookie.html':
                # send edited html
                if check_cookie(login_cache):
                    html = edit_user_cookie_html(login_cache)
                    send_http_response_html(connectionSocket, html)
                elif login_cache == "":
                    send_403(connectionSocket)
                else:
                    send_http_response(connectionSocket, '/index.html')

            else:
                send_404(connectionSocket)
        
        elif method == "POST":
            if url == '/storage':
                packet = get_post_data(connectionSocket)
                print('packet')
                print(packet)
                login_cache = process_storage(packet, login_cache, connectionSocket)


        connectionSocket.close()
    server_socket.close()


"""
entry point
"""
server_socket = init_socket()

run_socket_connection(server_socket)


