from functions.socket import *
from functions.filelist import *
from functions.http import *


server_socket = init_socket()

run_socket_connection(server_socket)

serverSocket.close()