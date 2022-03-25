from socket import *
from functions.files import *
from functions.view import *
from functions.http import *

def init_socket():
    serverPort = 10090
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('',serverPort))
    server_socket.listen(1)
    print('The server is ready to receive')
    return server_socket

def run_socket_connection(server_socket):
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
        # Put Exceptions on user input
        # when user logins
        if method == "GET":
            if url == '/storage.html':
                html = edit_storage_html()
                send_http_response_html(connectionSocket, html)
                
            elif '?' not in url:
                send_http_response(connectionSocket, url)
        

        elif method == "POST":
            if url == '/index.html':
                packet = get_post_data(connectionSocket)
                #print(packet)
                # get username and password
                user = re.compile(b'(?<=id=)(.*?)(?=\&)').search(packet).group(1)
                print(user)
                pw = re.compile(b'(?<=pw=)(.*?)').search(packet).group(1)
                print(pw)
                # Make personal storage
                make_personal_directory(user)
                # Save Cookie 
                save_cookie(user)
                # Edit storage.html
                html = edit_user_storage_html(user)
                send_http_response_html(connectionSocket, html)
            if url == '/storage.html':
                packet = get_post_data(connectionSocket)
                save_uploaded_file(packet)
                name = re.compile(b'name="submitted_file"; filename="(.+)"').search(packet).group(1)
                ok_reponse = b"Successfully uploaded " + name + b" to the server!"
                connectionSocket.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"+ok_reponse)   

        connectionSocket.close()
