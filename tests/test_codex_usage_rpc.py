"""Exercise real pipes: coalesced notifications, partial lines, and failures."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import time
import unittest

spec = importlib.util.spec_from_file_location(
    "collector", Path(__file__).resolve().parents[1] / "scripts/codex-usage-collector.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class RpcTests(unittest.TestCase):
    def request(self, output, timeout=0.3):
        code = "import os,sys,time; sys.stdin.readline(); " + output + "; time.sleep(2)"
        with subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, text=True) as proc:
            try:
                return collector.rpc_request(proc, 2, "account/read", timeout=timeout)
            finally:
                proc.kill()
                proc.wait()

    def test_notification_and_response_in_one_write(self):
        self.assertEqual(self.request(
            "os.write(1, b'{\"method\":\"account/updated\"}\\n{\"id\":2,\"result\":{}}\\n')"
        )["result"], {})

    def test_fragmented_response(self):
        self.assertEqual(self.request(
            "os.write(1, b'{\"id\":'); time.sleep(.03); os.write(1, b'2,\"result\":{}}\\n')"
        )["id"], 2)

    def test_partial_line_obeys_timeout(self):
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            self.request("os.write(1, b'{')", timeout=.1)
        self.assertLess(time.monotonic() - started, 1)

    def test_rpc_error(self):
        with self.assertRaisesRegex(RuntimeError, "account/read.*denied"):
            self.request("os.write(1, b'{\"id\":2,\"error\":{\"message\":\"denied\"}}\\n')")

    def test_eof(self):
        with self.assertRaisesRegex(RuntimeError, "closed its output"):
            self.request("sys.exit(0)")


if __name__ == "__main__":
    unittest.main()
