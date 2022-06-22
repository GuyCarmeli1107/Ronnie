import socket

HOST = "192.168.213.206"  # The server's hostname or IP address
PORT = 30000  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")