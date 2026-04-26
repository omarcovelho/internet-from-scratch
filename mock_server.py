import argparse

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="ifs mock server", version="0.1.0")


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "ok\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Protocol-strict HTTP/1.1 mock server (uvicorn + h11).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, http="h11", log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

