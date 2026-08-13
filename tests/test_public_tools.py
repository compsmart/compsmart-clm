from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from demo.clm_client import CLMClient
from demo.session_store import load_session, save_session


class Handler(BaseHTTPRequestHandler):
    session_creations = 0
    chat_authorizations = []

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
            type(self).session_creations += 1
            self.reply(201, {"token": "test-token", "expires_at": "2099-01-01T00:00:00Z"})
        else:
            type(self).chat_authorizations.append(self.headers.get("Authorization"))
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

    def setUp(self):
        Handler.session_creations = 0
        Handler.chat_authorizations = []

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

    def test_chat_resumes_saved_session_and_delete_forgets_it(self):
        root = Path(__file__).resolve().parents[1]
        base = f"http://127.0.0.1:{self.server.server_port}"
        with tempfile.TemporaryDirectory() as temporary_directory:
            session_file = Path(temporary_directory) / "sessions.json"
            command = [
                sys.executable,
                str(root / "demo" / "chat.py"),
                "--base-url",
                base,
                "--session-file",
                str(session_file),
            ]

            first = subprocess.run(
                command,
                cwd=root,
                input="My name is Brad\n/quit\n",
                text=True,
                capture_output=True,
                check=False,
            )
            second = subprocess.run(
                command,
                cwd=root,
                input="What's my name?\n/quit\n",
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(Handler.session_creations, 1)
            self.assertEqual(Handler.chat_authorizations, ["Bearer test-token"] * 2)
            self.assertTrue(session_file.is_file())
            self.assertIn("Resumed session", second.stdout)

            deleted = subprocess.run(
                command, cwd=root, input="/delete\n", text=True, capture_output=True, check=False
            )
            self.assertEqual(deleted.returncode, 0, deleted.stdout + deleted.stderr)
            self.assertFalse(session_file.exists())

    def test_expired_saved_session_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            session_file = Path(temporary_directory) / "sessions.json"
            save_session(
                session_file,
                "https://example.test",
                {"token": "expired-token", "expires_at": "2000-01-01T00:00:00Z"},
            )
            self.assertIsNone(load_session(session_file, "https://example.test"))

    def test_demo_files_are_grouped(self):
        root = Path(__file__).resolve().parents[1]
        for name in (
            "chat.py",
            "clm_client.py",
            "session_store.py",
            "verify_live.py",
            "verify_evidence.py",
        ):
            self.assertFalse((root / name).exists())
            self.assertTrue((root / "demo" / name).is_file())


if __name__ == "__main__":
    unittest.main()
