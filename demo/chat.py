from __future__ import annotations

import argparse
from pathlib import Path

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL
from session_store import default_session_file, forget_session, load_session, save_session


INVALID_SESSION_STATUSES = {401, 404, 410}


def create_and_save_session(client: CLMClient, session_file: Path) -> dict:
    session = client.create_session()
    try:
        save_session(session_file, client.base_url, session)
    except (OSError, ValueError) as error:
        raise CLMError(f"could not save session to {session_file}: {error}") from error
    return session


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with the Compsmart CLM preview")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--session-file",
        type=Path,
        help="session credential store (default: the current user's data directory)",
    )
    parser.add_argument(
        "--new-session",
        action="store_true",
        help="start a new anonymous session instead of resuming the saved one",
    )
    args = parser.parse_args()
    session_file = args.session_file or default_session_file()
    saved = None if args.new_session else load_session(session_file, args.base_url)
    client = CLMClient(args.base_url, token=saved["token"] if saved else None)
    try:
        session = saved or create_and_save_session(client, session_file)
        action = "Resumed session" if saved else "Session"
        print(f"{action} expires at {session['expires_at']}. Commands: /delete, /quit")
        while True:
            try:
                message = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not message:
                continue
            if message in {"/quit", "/exit"}:
                break
            if message == "/delete":
                try:
                    result = client.delete_session()
                except CLMError as error:
                    if error.status_code not in INVALID_SESSION_STATUSES:
                        raise
                    result = {"deleted": False, "detail": "session was already unavailable"}
                forget_session(session_file, client.base_url)
                print(result)
                break
            try:
                result = client.chat(message)
            except CLMError as error:
                if error.status_code not in INVALID_SESSION_STATUSES:
                    raise
                forget_session(session_file, client.base_url)
                client.token = None
                session = create_and_save_session(client, session_file)
                print(
                    "Saved session was no longer available; started a new one "
                    f"expiring at {session['expires_at']}."
                )
                result = client.chat(message)
            print(f"model> {result['reply']}")
            if result.get("learned"):
                print("       [learned]")
        return 0
    except CLMError as error:
        print(f"error: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

