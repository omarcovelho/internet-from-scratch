import socket
from http.message import HttpRequest, HttpResponse

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8082))

request = HttpRequest('GET', headers={'Host': 'localhost'})

client.sendall(request.to_bytes())
data = client.recv(1024)

response = HttpResponse.from_bytes(data)
print(f'Received from server (raw): \r\n=====================\r\n{response.to_bytes().decode()}\r\n=====================\r\n')

client.close()