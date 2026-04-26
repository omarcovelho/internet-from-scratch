# Copied from the repo's original top-level `http/message.py`.
# This lives under the package to avoid shadowing Python's stdlib `http`.

# RFC 9112 (HTTP/1.1 Message Syntax) glossary used by this file:
# - CRLF: Carriage Return + Line Feed, "\r\n" (line terminator on the wire)
# - SP:   Space character, " " (used to separate tokens in start-lines)
# - OWS:  Optional Whitespace (per RFC 9110), typically spaces/tabs around ":" in header fields
# - start-line: request-line (client) OR status-line (server), first line of an HTTP message
# - field-line: a single header field line: field-name ":" OWS field-value OWS
# - header section terminator: an empty line, i.e. CRLF CRLF
CRLF = "\r\n"
SP = " "
OWS = " "


CRLF_BYTES = b"\r\n"
CRLFCRLF_BYTES = b"\r\n\r\n"


# This abstracts the HTTP message syntax covered in §2 of RFC 9112.
#    
#  HTTP-message   = start-line CRLF
#                    *( field-line CRLF )
#                    CRLF
#                    [ message-body ]
#
class HttpMessage:
    http_version = "HTTP/1.1"

    def __init__(self, headers=None):
        self.headers = headers if headers is not None else {}

    def start_line(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _format_field_lines(headers: dict) -> str:
        # RFC 9112 §5 - field-line = field-name ":" OWS field-value OWS
        return CRLF.join(f"{k}:{OWS}{v}{OWS}" for k, v in headers.items())

    def to_bytes(self) -> bytes:
        # RFC 9112 §2.1 - header section ends with CRLF CRLF
        # HTTP-message   = start-line CRLF
        #                *( field-line CRLF )
        #                CRLF
        #                [ message-body ]
        start_line = self.start_line()
        header_lines = self._format_field_lines(self.headers)
        if header_lines:
            return f"{start_line}{CRLF}{header_lines}{CRLF}{CRLF}".encode()
        return f"{start_line}{CRLF}{CRLF}".encode()

    @staticmethod
    # Split HTTP message into head and rest, where head is the start-line and the field-lines.
    # The rest is the message-body.
    # CRLFCRLF_BYTES is the CRLF CRLF terminator (two line breaks).
    # See whole http message structure below: 
    #  HTTP-message   = start-line CRLF
    #                    *( field-line CRLF )
    #                    CRLF
    #                    [ message-body ]
    #
    def split_head(data: bytes) -> tuple[str, list[str]]:
        if CRLFCRLF_BYTES not in data:
            raise ValueError("Invalid HTTP message: missing CRLFCRLF terminator")

        head, rest = data.split(CRLFCRLF_BYTES, 1)

        lines = head.split(CRLF_BYTES)

        start_line = lines[0].decode(errors="strict")
        field_lines = [ln.decode(errors="strict") for ln in lines[1:] if ln]
        return start_line, field_lines

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
    def __init__(self, method: str, path: str = "/", host: str = "127.0.0.1", proxy: str = None, headers: dict[str, str] | None = None):
        method = method.upper()
        if method != "GET":
            raise ValueError("Only GET requests are supported for now")

        super().__init__(headers=headers)
        self.host = host
        self.method = method
        self.path = path
        self.proxy = proxy

        # RFC 9112 §3.2.2 - proxy, use absolute-form, host becomes the proxy host
        if(proxy):
            self.headers["Host"] = proxy
        else:
            self.headers["Host"] = host


    def start_line(self) -> str:
        # RFC 9112 §3 - request-line = method SP request-target SP HTTP-version
        # RFC 9112 §3.1 - method = token defined in section 9 of RFC 9110
        method = self.method
        # RFC 9112 §2.3 - HTTP-version = HTTP-version-number SP HTTP-version-token
        # (using hardcoded string in this case)
        http_version = self.http_version

        if self.proxy:
            # RFC 9112 §3.2.2 - proxy, use absolute-form
            #  absolute-form  = absolute-URI
            request_target = self.host + self.path
        else:
            # RFC 9112 §3.2.1 - no proxy, use origin-form
            #  origin-form    = absolute-path [ "?" query ]
            request_target = self.path
        
        #RFC 9112 §3 - request-line = method SP request-target SP HTTP-version
        request_line = f"{method}{SP}{request_target}{SP}{http_version}"
        return request_line

    @classmethod
    def from_bytes(cls, data: bytes) -> "HttpRequest":
        start_line, header_lines = cls.split_head(data)
        start_line_parts = start_line.split(" ")
        if len(start_line_parts) != 3:
            raise ValueError(f"Invalid request-line: {start_line!r}")
        method, path, version = start_line_parts
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
        # RFC 9112 §4 - status-line = HTTP-version-number SP status-code SP [reason-phrase]

        # RFC 9112 §2.3 - HTTP-version = HTTP-version-number SP HTTP-version-token
        # (using hardcoded string in this case)
        http_version = self.http_version
        # RFC 9112 §4.1 - status-code = 3DIGIT
        # defined in section 15 of RFC 9110 - HTTP Status Codes
        status_code = self.status_code

        # RFC 9112 §4.2 - reason-phrase  = 1*( HTAB / SP / VCHAR / obs-text )
        # This is not considered by the client, only for informative purposes, and convention is to send http code descriptions
        reason_phrase = self.reason_phrase

        return f"{http_version} {status_code} {reason_phrase}"

    @classmethod
    def from_bytes(cls, data: bytes) -> "HttpResponse":
        start_line, header_lines = cls.split_head(data)
        parts = start_line.split(f"{SP}", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid status-line: {start_line!r}")
        version, status_code, reason = parts
        if version != cls.http_version:
            raise ValueError(f"Unsupported HTTP version: {version!r}")
        headers = cls.parse_headers(header_lines)
        return cls(status_code=int(status_code), reason_phrase=reason, headers=headers)

