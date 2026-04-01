#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# ///
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class DemoRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


def parse_args():
    parser = argparse.ArgumentParser(description="Serve the PyScript demo locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to.")
    parser.add_argument(
        "--directory",
        default="pyscript_panel_plotly_demo",
        help="Directory to serve. Defaults to the demo app.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.directory).resolve()
    if not root.exists():
        raise SystemExit(f"Directory does not exist: {root}")

    handler = partial(DemoRequestHandler, directory=str(root))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Serving {root}")
    print(f"Open {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
