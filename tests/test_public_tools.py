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
from demo.learner_store import load_learner, save_learner


class Handler(BaseHTTPRequestHandler):
    session_creations = 0
    session_requests = []
    chat_authorizations = []
    delete_paths = []

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
        payload = json.loads(self.rfile.read(length)) if length else {}
        if self.path == "/v1/sessions":
            type(self).session_creations += 1
            type(self).session_requests.append(payload)
            self.reply(
                201,
                {
                    "token": f"test-session-{self.session_creations}",
                    "learner_token": payload.get("learner_token", "test-learner"),
                    "expires_at": "2099-01-01T00:00:00Z",
                },
            )
        else:
            type(self).chat_authorizations.append(self.headers.get("Authorization"))
            self.reply(200, {"reply": "remembered", "learned": True, "expires_at": "2099-01-01T00:00:00Z"})

    def do_GET(self):
        self.reply(200, {"status": "ok", "model": "compsmart-clm-preview"})

    def do_DELETE(self):
        type(self).delete_paths.append(self.path)
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
        Handler.session_requests = []
        Handler.chat_authorizations = []
        Handler.delete_paths = []

    def test_client_contract(self):
        base = f"http://127.0.0.1:{self.server.server_port}"
        client = CLMClient(base)
        self.assertEqual(client.health()["status"], "ok")
        self.assertEqual(client.create_session()["token"], "test-session-1")
        self.assertTrue(client.chat("hello")["learned"])
        self.assertTrue(client.delete_session()["deleted"])
        client.create_session(learner_token="test-learner")
        self.assertTrue(client.delete_learner()["deleted"])

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

    def test_chat_starts_fresh_session_with_saved_learner(self):
        root = Path(__file__).resolve().parents[1]
        base = f"http://127.0.0.1:{self.server.server_port}"
        with tempfile.TemporaryDirectory() as temporary_directory:
            learner_file = Path(temporary_directory) / "sessions.json"
            command = [
                sys.executable,
                str(root / "demo" / "chat.py"),
                "--base-url",
                base,
                "--learner-file",
                str(learner_file),
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
            self.assertEqual(Handler.session_creations, 2)
            self.assertEqual(Handler.session_requests, [{}, {"learner_token": "test-learner"}])
            self.assertEqual(
                Handler.chat_authorizations,
                ["Bearer test-session-1", "Bearer test-session-2"],
            )
            self.assertTrue(learner_file.is_file())
            self.assertNotIn("Resumed session", second.stdout)

            deleted = subprocess.run(
                command, cwd=root, input="/delete\n", text=True, capture_output=True, check=False
            )
            self.assertEqual(deleted.returncode, 0, deleted.stdout + deleted.stderr)
            self.assertTrue(learner_file.exists())

            forgotten = subprocess.run(
                command, cwd=root, input="/forget\n", text=True, capture_output=True, check=False
            )
            self.assertEqual(forgotten.returncode, 0, forgotten.stdout + forgotten.stderr)
            self.assertFalse(learner_file.exists())
            self.assertEqual(
                Handler.delete_paths,
                ["/v1/sessions/current", "/v1/learners/current"],
            )

    def test_old_session_credential_is_migrated_to_learner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            session_file = Path(temporary_directory) / "sessions.json"
            session_file.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "sessions": {
                            "https://example.test": {
                                "token": "old-session-token",
                                "expires_at": "2099-01-01T00:00:00Z",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                load_learner(session_file, "https://example.test"),
                {"source_session_token": "old-session-token"},
            )
            save_learner(session_file, "https://example.test", "new-learner-token")
            self.assertEqual(
                load_learner(session_file, "https://example.test"),
                {"learner_token": "new-learner-token"},
            )

    def test_demo_files_are_grouped(self):
        root = Path(__file__).resolve().parents[1]
        for name in (
            "chat.py",
            "clm_client.py",
            "learner_store.py",
            "verify_live.py",
            "verify_evidence.py",
        ):
            self.assertFalse((root / name).exists())
            self.assertTrue((root / "demo" / name).is_file())


if __name__ == "__main__":
    unittest.main()
