class HttpRequest:
    def __init__(self, method, path="/", headers=None, body=None):
        self.method = method
        self.path = path
        self.headers = headers if headers is not None else {}
        self.body = body

    def toBytes(self):
        # RFC 9112 §3 - request-line = method SP request-target SP HTTP-version
        line = f"{self.method} {self.path} HTTP/1.1"
        # RFC 9112 §5 - field-line = field-name ":" OWS field-value OWS
        header_lines = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
        # RFC 9112 §2.1 - headers and body separated by empty line (CRLF CRLF)
        return f"{line}\r\n{header_lines}\r\n\r\n{self.body}".encode()

class HttpResponse:
    def __init__(self, status_code, reason_phrase, headers=None, body=None):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.headers = headers if headers is not None else {}
        self.body = body

    def toBytes(self):
        # RFC 9112 §3 - status-line = HTTP-version SP status-code SP reason-phrase
        line = f"HTTP/1.1 {self.status_code} {self.reason_phrase}"
        # RFC 9112 §5 - field-line = field-name ":" OWS field-value OWS
        header_lines = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
        # RFC 9112 §2.1 - headers and body separated by empty line (CRLF CRLF)
        return f"{line}\r\n{header_lines}\r\n\r\n{self.body}".encode()