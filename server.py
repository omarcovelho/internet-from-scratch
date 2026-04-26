import argparse
import socket

from ifs.ifshttp.message import HttpRequest, HttpResponse


def main() -> int:
    parser = argparse.ArgumentParser(description="internet-from-scratch: demo HTTP server (OS TCP)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument("--once", action="store_true", help="serve one request then exit")
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen(1)

    print(f"Server is listening on {args.host}:{args.port}...")
    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address} has been established.")

        data = client_socket.recv(1024)
        req = HttpRequest.from_bytes(data)
        print(
            "Received from client (raw): \r\n=====================\r\n"
            f"{req.to_bytes().decode()}\r\n=====================\r\n"
        )

        client_socket.sendall(HttpResponse(200, "OK", headers={"Content-Type": "text/plain"}).to_bytes())
        client_socket.close()

        if args.once:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())

