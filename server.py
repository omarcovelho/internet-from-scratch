import socket

from http.message import HttpResponse

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 8082))
server.listen(1)

print('Server is listening on port 8082...')
while True:
    client_socket, client_address = server.accept()
    print(f'Connection from {client_address} has been established.')

    data = client_socket.recv(1024)
    print(f'Received from client: \r\n=====================\r\n{data.decode()}\r\n=====================\r\n')

    client_socket.sendall(HttpResponse(200, 'OK', headers={'Content-Type': 'text/plain'}, body='Hello, HTTP!').toBytes())
    client_socket.close()
