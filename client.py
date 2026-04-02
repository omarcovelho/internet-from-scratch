import socket
from http.message import HttpRequest

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8082))

request = HttpRequest('GET', headers={'Host': 'localhost'}, body=None)

client.sendall(request.toBytes())
response = client.recv(1024)
print(f'Received from server: \r\n=====================\r\n{response.decode()}\r\n=====================\r\n')

client.close()