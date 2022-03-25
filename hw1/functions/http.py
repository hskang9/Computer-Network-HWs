from socket import *
import re
from time import time

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