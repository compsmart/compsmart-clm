from __future__ import annotations

import argparse

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with the Compsmart CLM preview")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    client = CLMClient(args.base_url)
    try:
        session = client.create_session()
        print(f"Session expires at {session['expires_at']}. Commands: /delete, /quit")
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
                print(client.delete_session())
                break
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

