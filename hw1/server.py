from multiprocessing.reduction import send_handle
from socket import *
from unittest import skip
import re

serverPort = 10090
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

def send_http_response(socket, filename):
    try:
        htmlFS = open('html' + filename)
        content = htmlFS.read()
        htmlFS.close()
        response = 'HTTP/1.0 200 Ok\n\n' + content
        socket.sendall(response.encode())
    except IOError:
        print("html file does not exist on:", filename)

def get_data(conn):
    data = b""
    while True:
        chunk = conn.recv(1024)
        if len(chunk) < 1024:
            return data + chunk
        else:
            data += chunk

def save_file(packet):
    name = re.compile(b'name="uploadedfile"; filename="(.+)"').search(packet).group(1)
    data = re.compile(b"WebKitFormBoundary((\n|.)*)Content-Type.+\n.+?\n((\n|.)*)([\-]+WebKitFormBoundary)?")
    with open(name, "wb") as file:
        file.write(data.search(packet).group(3))

while True:
    connectionSocket, addr = serverSocket.accept()
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
        if url == '/index.html?id=':
            send_http_response(connectionSocket, '/storage.html')

        elif '?' not in url:
            send_http_response(connectionSocket, url)
    elif method == "POST":
        packet = get_data(connectionSocket)
        save_file(packet)
        print(packet)
        ok_reponse = b"Successfully upload %d bytes to the server!" % len(packet)
        connectionSocket.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"+ok_reponse)    

    connectionSocket.close()



serverSocket.close()