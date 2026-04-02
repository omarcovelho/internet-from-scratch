# RFC 9112 (HTTP/1.1 Message Syntax) glossary used by this file:
# - CRLF: Carriage Return + Line Feed, "\r\n" (line terminator on the wire)
# - SP:   Space character, " " (used to separate tokens in start-lines)
# - OWS:  Optional Whitespace (per RFC 9110), typically spaces/tabs around ":" in header fields
# - start-line: request-line (client) OR status-line (server), first line of an HTTP message
# - field-line: a single header field line: field-name ":" OWS field-value OWS
# - header section terminator: an empty line, i.e. CRLF CRLF
CRLF = "\r\n"
CRLF_BYTES = b"\r\n"
CRLFCRLF_BYTES = b"\r\n\r\n"


class HttpMessage:
    http_version = "HTTP/1.1"

    def __init__(self, headers=None):
        self.headers = headers if headers is not None else {}

    def start_line(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _format_header_lines(headers: dict) -> str:
        # RFC 9112 §5 - field-line = field-name ":" OWS field-value OWS
        return CRLF.join(f"{k}: {v}" for k, v in headers.items())

    def to_bytes(self) -> bytes:
        # RFC 9112 §2.1 - header section ends with CRLF CRLF
        line = self.start_line()
        header_lines = self._format_header_lines(self.headers)
        if header_lines:
            return f"{line}{CRLF}{header_lines}{CRLF}{CRLF}".encode()
        return f"{line}{CRLF}{CRLF}".encode()


    @staticmethod
    def split_head(data: bytes) -> tuple[str, list[str]]:
        if CRLFCRLF_BYTES not in data:
            raise ValueError("Invalid HTTP message: missing CRLFCRLF terminator")

        head, rest = data.split(CRLFCRLF_BYTES, 1)
        
        lines = head.split(CRLF_BYTES)
        if not lines or lines[0] == b"":
            raise ValueError("Invalid HTTP message: missing start-line")

        start_line = lines[0].decode(errors="strict")
        header_lines = [ln.decode(errors="strict") for ln in lines[1:] if ln]
        return start_line, header_lines

    @staticmethod
    def parse_headers(header_lines: list[str]) -> dict[str, str]:
        headers: dict[str, str] = {}
        for line in header_lines:
            if ":" not in line:
                raise ValueError(f"Invalid header field-line: {line!r}")
            name, value = line.split(":", 1)
            headers[name.strip()] = value.strip()
        return headers


class HttpRequest(HttpMessage):
    def __init__(self, method: str, path: str = "/", headers=None):
        method = method.upper()
        if method != "GET":
            raise ValueError("Only GET requests are supported for now")

        super().__init__(headers=headers)
        self.method = method
        self.path = path

    def start_line(self) -> str:
        # RFC 9112 §3 - request-line = method SP request-target SP HTTP-version
        return f"{self.method} {self.path} {self.http_version}"

    @classmethod
    def from_bytes(cls, data: bytes) -> "HttpRequest":
        start_line, header_lines = cls.split_head(data)
        parts = start_line.split(" ")
        if len(parts) != 3:
            raise ValueError(f"Invalid request-line: {start_line!r}")
        method, path, version = parts
        if version != cls.http_version:
            raise ValueError(f"Unsupported HTTP version: {version!r}")
        headers = cls.parse_headers(header_lines)
        return cls(method=method, path=path, headers=headers)


class HttpResponse(HttpMessage):
    def __init__(self, status_code: int, reason_phrase: str, headers=None):
        super().__init__(headers=headers)
        self.status_code = int(status_code)
        self.reason_phrase = reason_phrase

    def start_line(self) -> str:
        # RFC 9112 §3 - status-line = HTTP-version SP status-code SP reason-phrase
        return f"{self.http_version} {self.status_code} {self.reason_phrase}"

    @classmethod
    def from_bytes(cls, data: bytes) -> "HttpResponse":
        start_line, header_lines = cls.split_head(data)
        parts = start_line.split(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid status-line: {start_line!r}")
        version, status_code, reason = parts
        if version != cls.http_version:
            raise ValueError(f"Unsupported HTTP version: {version!r}")
        headers = cls.parse_headers(header_lines)
        return cls(status_code=int(status_code), reason_phrase=reason, headers=headers)