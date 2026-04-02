import socket

from http.message import HttpRequest, HttpResponse

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 8082))
server.listen(1)

print('Server is listening on port 8082...')
while True:
    client_socket, client_address = server.accept()
    print(f'Connection from {client_address} has been established.')

    data = client_socket.recv(1024)
    req = HttpRequest.from_bytes(data)
    print(f'Received from client (raw): \r\n=====================\r\n{req.to_bytes().decode()}\r\n=====================\r\n')

    client_socket.sendall(HttpResponse(200, 'OK', headers={'Content-Type': 'text/plain'}).to_bytes())
    client_socket.close()
