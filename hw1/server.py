from socket import *
from os import listdir, mkdir, getcwd, remove
from os.path import join, join
import re
from time import time
from urllib.parse import unquote

"""
file related functions
"""

def get_file_list(path):
    return listdir(path)

def make_directory(username):
    try:
        # make a dir inside files/ directory
        curr_dir = getcwd()
        result = join(curr_dir, f"{username}")
        mkdir(result, 0o777)
    except FileExistsError:
        print(f"user {username} directory already exists, moving on")

def save_cookie(user):
    # check if cookies directory exists
    try:
        with open(f"cookies/{user}", "wb") as file:
            timestamp = f"{time()}"
            file.write(timestamp.encode())
    except IOError:
        print("cookies/ directory does not exist, making one")
        make_directory("cookies")
    finally:
        with open(f"cookies/{user}", "wb") as file:
            timestamp = f"{time()}"
            file.write(timestamp.encode())


def delete_file(user, file):
    remove(f"{user}/{file}")

"""
http related functions
"""

def recv_http_data(conn):
    data = b""
    while True:
        chunk = conn.recv(1024)
        if len(chunk) < 1024:
            return data + chunk
        else:
            data += chunk

def send_http_response(socket, filename):
    try:
        htmlFS = open(filename)
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
    cut_front = re.compile(b"WebKitFormBoundary((\n|.)*)Content-Type.+\n.+?\n((\n|.)*)\r\n------WebKitFormBoundary?").search(packet).group(3)
    # save file
    print(cut_front)
    with open(f"{user}/{name.decode('UTF-8')}", "wb") as file:
        file.write(cut_front)

def check_cookie(user):
    if user == "":
        return False
    cookieFS = open('cookies' + f'/{user}')
    content = cookieFS.read()
    cookieFS.close()
    diff = (time() - float(content))
    return diff <= 120

"""
view related functions
"""

def edit_user_storage_html(user):
    # get list of files in files directory
    filelist = get_file_list(f'{user}')
    # edit storage.html
    htmlFS = open('html' + '/storage.html')
    content = htmlFS.read()
    htmlFS.close()

    # replace user1 with received username
    pattern = re.compile(r"user1")
    change_user = pattern.sub(user, content)
    
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"\<ul[^\>]*\>\s*\<\/ul\>")
    # replace it with mad html
    html = "<ul>"
    for i in filelist:
        list_element = f"<li>{i} <a href=\"/{user}/{i}\" download><button>Download</button></a> <a href=\"/delete/{user}/{i}\"><button>Delete</button></a> </li>"
        html+=list_element
    html+="</ul>"
    result = pattern.sub(html, change_user)
    return result

def edit_user_cookie_html(user):
    # edit cookie.html
    htmlFS = open('html' + '/cookie.html')
    content = htmlFS.read()
    htmlFS.close()

    # replace user1 with received username
    pattern = re.compile(r"user1")
    change_user = pattern.sub(user, content)
    
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"27")
    cookieFS = open('cookies/' + user)
    content = cookieFS.read()
    cookieFS.close()
   
    # replace time in html
    tdiff = time() - float(content)
    left = str(120 - tdiff)
    result = pattern.sub(left, change_user)
    return result

"""
socket related functions(controller)
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
        if login_cache == "":
            send_403(connectionSocket)
        else:
            print("upload request from /storage, change to upload")
            # get http post file inputs
            file = recv_http_data(connectionSocket)
            login_cache = process_upload(file, login_cache, connectionSocket)
    return login_cache

def process_login(packet, connectionSocket):
    # get username and password
    user = re.compile(b'(?<=name="id"\\r\\n\\r\\n)(.*?)(?=\\r\\n------)').search(packet).group(1).decode("UTF-8")
    pw = re.compile(b'(?<=name="pw"\\r\\n\\r\\n)(.*?)(?=\\r\\n------)').search(packet).group(1).decode("UTF-8")
    # Make personal storage
    make_directory(user)
    # Save Cookie 
    save_cookie(user)
     # Edit storage.html
    html = edit_user_storage_html(user)
    send_http_response_html(connectionSocket, html)
    return user

def process_upload(packet, login_cache, connectionSocket):
    print(packet)
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
        request = recv_http_data(connectionSocket)
        headers = request.split(b'\n')
        #print(headers[0]) # <CODE(GET/PUT/POST/DELETE)> <URL> <HTTP Connection version>
        method =  headers[0].split()[0]  
        url = headers[0].split()[1] 
    
        # Router
        if method == b"GET":
            # user storage page
            if url == b'/storage':
                # check cookie
                if check_cookie(login_cache):
                     html = edit_user_storage_html(login_cache)
                     send_http_response_html(connectionSocket, html)
                else:
                    login_cache = ""
                    send_403(connectionSocket)
                
            # index page
            elif url == b"/":
                send_http_response(connectionSocket, 'html/index.html')
            
            # delete file in user storage
            elif url.startswith(b'/delete'):
                if login_cache == "" or check_cookie(login_cache) == False:
                    send_403(connectionSocket)
                else:
                    # unquote url input to unicode string
                    url_input = unquote(url).split('/')
                    if len(url_input) > 4:
                        send_404(connectionSocket)
                    else:
                        user, file = url_input[2], url_input[3] 
                        # delete file 
                        delete_file(user, file)
                        html = edit_user_storage_html(login_cache)
                        send_http_response_html(connectionSocket, html)
            
            # user file storage access
            elif unquote(url).split('/')[1] in get_file_list("./"):
                url_input = unquote(url).split('/')
                user, file = url_input[1], url_input[2] 
                # if not logged in or tries to access other user's file, show 403 error as PA1 describes
                if login_cache != user:
                    send_403(connectionSocket)
                else:
                    if len(url_input) > 3:
                        send_404(connectionSocket)
                    else:
                        # retrieve file
                        send_http_response(connectionSocket, f'{user}/{file}')
                    
            # cookie management
            elif url == b'/cookie.html':
                # send edited html
                if check_cookie(login_cache):
                    html = edit_user_cookie_html(login_cache)
                    send_http_response_html(connectionSocket, html)
                elif login_cache == "":
                    send_403(connectionSocket)
                else:
                    send_http_response(connectionSocket, 'html/index.html')

            else:
                send_404(connectionSocket)
        
        elif method == b"POST":
            if url == b'/storage':
                login_cache = process_storage(request, login_cache, connectionSocket)


        connectionSocket.close()
    server_socket.close()


"""
entry point
"""
server_socket = init_socket()

run_socket_connection(server_socket)


