from socket import *

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
            if url == '/index.html?id=':
                send_http_response(connectionSocket, '/storage.html')

            elif '?' not in url:
                send_http_response(connectionSocket, url)
        
            elif url == '/storage.html':
                try:
                    # get list of files in files directory
                    filelist = get_the_file_list('../files')
                    # edit storage.html
                    htmlFS = open('html' + filename)
                    send_http_response(connectionSocket, 'storage.html')
                except IOError:
                    print("files does not exist on files directory")

        elif method == "POST":
            if url == 'storage.html':
                packet = get_post_data(connectionSocket)
                save_uploaded_file(f"files/{packet}")
                print(packet)
                ok_reponse = b"Successfully upload %d bytes to the server!" % len(packet)
                connectionSocket.sendall(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"+ok_reponse)   

        connectionSocket.close()
