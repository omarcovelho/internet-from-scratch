import argparse
import socket

from ifs.ifshttp.message import HttpRequest, HttpResponse


def main() -> int:
    parser = argparse.ArgumentParser(description="internet-from-scratch: demo HTTP client (OS TCP)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument("--path", default="/")
    parser.add_argument("--proxy", default="127.0.0.1")
    args = parser.parse_args()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((args.host, args.port))

    request = HttpRequest("GET", path="/", host="127.0.0.1")
    print(
        "Sending to server (raw): \r\n=====================\r\n"
        f"{request.to_bytes().decode()}\r\n=====================\r\n"
    )
    client.sendall(request.to_bytes())

    data = client.recv(1024)
    response = HttpResponse.from_bytes(data)
    print(
        "Received from server (raw): \r\n=====================\r\n"
        f"{response.to_bytes().decode()}\r\n=====================\r\n"
    )

    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

