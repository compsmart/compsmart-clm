from __future__ import annotations

import argparse
from pathlib import Path

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL
from learner_store import default_learner_file, forget_learner, load_learner, save_learner


INVALID_SESSION_STATUSES = {401, 404, 410}


def create_session(client: CLMClient, learner_file: Path, saved: dict | None) -> dict:
    session = client.create_session(**(saved or {}))
    try:
        save_learner(learner_file, client.base_url, session.get("learner_token", ""))
    except (OSError, ValueError) as error:
        raise CLMError(f"could not save learner identity to {learner_file}: {error}") from error
    return session


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with the Compsmart CLM preview")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--learner-file",
        "--session-file",
        dest="learner_file",
        type=Path,
        help="learner credential store (default: the current user's data directory)",
    )
    args = parser.parse_args()
    learner_file = args.learner_file or default_learner_file()
    saved = load_learner(learner_file, args.base_url)
    client = CLMClient(args.base_url)
    try:
        session = create_session(client, learner_file, saved)
        saved = {"learner_token": session["learner_token"]}
        print(f"Session expires at {session['expires_at']}. Commands: /delete, /forget, /quit")
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
                print(result)
                break
            if message == "/forget":
                try:
                    result = client.delete_learner()
                finally:
                    forget_learner(learner_file, client.base_url)
                print(result)
                break
            try:
                result = client.chat(message)
            except CLMError as error:
                if error.status_code not in INVALID_SESSION_STATUSES:
                    raise
                session = create_session(client, learner_file, saved)
                saved = {"learner_token": session["learner_token"]}
                print(
                    "Session was no longer available; started a new one "
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

