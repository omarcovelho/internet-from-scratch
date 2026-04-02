# internet-from-scratch

Reimplementing the internet protocol stack from HTTP down to IP, one layer at a time.

The goal is to understand what actually happens when you type a URL — not by reading about it, but by writing every layer yourself. Each phase peels away one more abstraction that the OS normally handles for you, replacing it with code you own and can observe.

## Architecture

The project is built around a `Transport` interface that decouples the application layer from whatever sits below. The HTTP client and server always call `transport.send()` and `transport.recv()`. What changes between phases is what's behind that interface.

Every layer logs what it does. In Phase 1 the TCP logs are shallow — just byte counts — because the OS is doing the real work. As you implement lower layers, the logs get richer because the code is yours. Sequence numbers, ACKs, retransmissions, IP headers — all visible once you own the layer.

## Phases

### Phase 1 — HTTP over OS TCP ← *current*
HTTP client and server built on raw sockets (`SOCK_STREAM`). Parsing and serializing HTTP/1.1 requests and responses per [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html). The OS kernel handles TCP — it's a black box at this stage.

### Phase 2 — TCP over UDP
Replace `SOCK_STREAM` with `SOCK_DGRAM` and implement TCP reliability by hand: segmentation, sequence numbers, ACKs, retransmission, congestion control. The HTTP layer doesn't change — only the `Transport` implementation is swapped. Follows [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html).

### Phase 3 — Wire simulation
A UDP proxy between client and server that injects network entropy: packet loss, latency, jitter, corruption, reordering. This is what makes Phase 2 honest — without it, reliability code is never truly tested.

### Phase 4 — IP layer (raw sockets)
Craft IP packets manually using raw sockets. Headers, TTL, fragmentation — all hand-built. At this point, almost nothing is left to the kernel.

## Running

Start the server:
```bash
python server.py
```

Send a request:
```bash
python client.py
```

## References

- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html) — HTTP/1.1 Message Syntax
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) — HTTP Semantics
- [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html) — Transmission Control Protocol (TCP)
- [RFC 791](https://www.rfc-editor.org/rfc/rfc791.html) — Internet Protocol (IP)
