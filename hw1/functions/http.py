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

def send_http_response(socket, filename):
    try:
        htmlFS = open('html' + filename)
        content = htmlFS.read()
        htmlFS.close()
        response = 'HTTP/1.0 200 Ok\n\n' + content
        socket.sendall(response.encode())
    except IOError:
        print("html file does not exist on:", filename)

def save_uploaded_file(packet):
    name = re.compile(b'name="uploadedfile"; filename="(.+)"').search(packet).group(1)
    data = re.compile(b"WebKitFormBoundary((\n|.)*)Content-Type.+\n.+?\n((\n|.)*)([\-]+WebKitFormBoundary)?")
    with open(name, "wb") as file:
        file.write(data.search(packet).group(3))