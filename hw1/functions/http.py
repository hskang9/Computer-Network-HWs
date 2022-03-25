from socket import *
import re

def get_post_data(conn):
    data = b""
    while True:
        chunk = conn.recv(1024)
        if len(chunk) < 1024:
            return data + chunk
        else:
            data += chunk
    return data

def send_http_response(socket, filename):
    try:
        htmlFS = open('html' + filename)
        content = htmlFS.read()
        htmlFS.close()
        response = 'HTTP/1.0 200 Ok\n\n' + content
        socket.sendall(response.encode())
    except IOError:
        print("html file does not exist on:", filename)

def send_http_response_html(socket, html):
    response = 'HTTP/1.0 200 Ok\n\n' + html
    socket.sendall(response.encode())

def save_uploaded_file(packet):
    print("input")
    print(packet)
    name = re.compile(b'name="submitted_file"; filename="(.+)"').search(packet).group(1)
    data = re.compile(b"WebKitFormBoundary((\n|.)*)Content-Type.+\n.+?\n((\n|.)*)([\-]+WebKitFormBoundary)?")
    with open(f"files/{name.decode()}", "wb") as file:
        file.write(data.search(packet).group(3))