from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading
import unittest

from demo.clm_client import CLMClient


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        if self.path == "/v1/sessions":
            self.reply(201, {"token": "test-token", "expires_at": "2099-01-01T00:00:00Z"})
        else:
            self.reply(200, {"reply": "remembered", "learned": True, "expires_at": "2099-01-01T00:00:00Z"})

    def do_GET(self):
        self.reply(200, {"status": "ok", "model": "compsmart-clm-preview"})

    def do_DELETE(self):
        self.reply(200, {"deleted": True})


class PublicToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_client_contract(self):
        base = f"http://127.0.0.1:{self.server.server_port}"
        client = CLMClient(base)
        self.assertEqual(client.health()["status"], "ok")
        self.assertEqual(client.create_session()["token"], "test-token")
        self.assertTrue(client.chat("hello")["learned"])
        self.assertTrue(client.delete_session()["deleted"])

    def test_published_evidence_verifier(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "demo" / "verify_evidence.py")],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"passed": true', result.stdout.lower())

    def test_demo_files_are_grouped(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("chat.py", "clm_client.py", "verify_live.py", "verify_evidence.py"):
            self.assertFalse((root / name).exists())
            self.assertTrue((root / "demo" / name).is_file())


if __name__ == "__main__":
    unittest.main()
