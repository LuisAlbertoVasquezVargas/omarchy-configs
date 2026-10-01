#!/usr/bin/python3
"""Use Omarchy's installed collector with a deadline-safe JSON-lines reader."""

import json
import os
from pathlib import Path
import runpy
import select
import time


def rpc_request(proc, request_id, method, params=None, timeout=8):
    proc.stdin.write(json.dumps({
        "id": request_id, "method": method, "params": params or {},
    }) + "\n")
    proc.stdin.flush()
    # Never mix TextIOWrapper.readline() with select(): readline may prefetch
    # several messages, leaving select watching an empty OS pipe. Keep framing
    # here instead, including incomplete lines and messages for the next call.
    pending = getattr(proc, "_omarchy_rpc_pending", b"")
    deadline = time.monotonic() + timeout
    while True:
        while b"\n" in pending:
            line, pending = pending.split(b"\n", 1)
            proc._omarchy_rpc_pending = pending
            try:
                message = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                continue
            if not isinstance(message, dict) or message.get("id") != request_id:
                continue
            if "error" in message:
                error = message["error"]
                raise RuntimeError(f"{method}: {error}")
            return message
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(method)
        ready, _, _ = select.select([proc.stdout], [], [], remaining)
        if not ready:
            raise TimeoutError(method)
        chunk = os.read(proc.stdout.fileno(), 65536)
        if not chunk:
            raise RuntimeError(f"{method}: Codex app-server closed its output")
        pending += chunk
        proc._omarchy_rpc_pending = pending


def load_collector():
    source = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy")) / "bin/omarchy-agent-usage-codex"
    module = runpy.run_path(str(source))
    # runpy's returned mapping is not necessarily a function's globals mapping.
    module["fetch_codex_rpc"].__globals__["rpc_request"] = rpc_request
    return module


if __name__ == "__main__":
    load_collector()["main"]()
