from __future__ import annotations

import argparse
import json
from pathlib import Path

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL
from learner_store import default_learner_file, forget_learner, load_learner, save_learner


INVALID_SESSION_STATUSES = {401, 404, 410}


HELP = """Commands:
  /model    base model, mechanism, learned-state type and size
  /status   this learner's revision, state hash and commitments
  /history  recent prompts, replies, learning and reload events
  /verify   replay the accepted commitments and check integrity
  /reload   unload state, restore it from disk, and print the proof trace
  /new      start a clean conversation with the same learner
  /delete   delete this conversation; keep learned state
  /forget   permanently delete this learner and its conversations
  /quit     exit
"""


def human_bytes(value: int | float | None) -> str:
    amount = float(value or 0)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(amount) < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def short_hash(value: str | None) -> str:
    return value[:12] if value else "—"


def print_model(value: dict) -> None:
    parameters = value.get("parameters", {})
    learned = value.get("learned_state", {})
    print(f"model> {value.get('model')} · {value.get('architecture')} · {value.get('dtype')}")
    print(f"       {value.get('mechanism')}")
    print(f"       base files {human_bytes(value.get('base_files_bytes'))}; "
          f"{int(parameters.get('total', 0)):,} parameters")
    print(f"       learned state {learned.get('type')} · {human_bytes(learned.get('bytes'))} · "
          f"{short_hash(learned.get('sha256'))}")
    print(f"       parameter updates: {value.get('parameter_updating')}; retrieval: {value.get('retrieval_used')}")


def print_session(value: dict) -> None:
    learned = value.get("learned_state", value.get("adapter", {}))
    print(f"model> revision {learned.get('revision', 0)} · {value.get('active_commitments', 0)} active commitments")
    print(f"       state {short_hash(learned.get('sha256'))} · {human_bytes(learned.get('bytes'))}")
    print(f"       reload {value.get('learner', {}).get('last_reload') or 'not yet'}")


def print_history(value: dict) -> None:
    rows = value.get("events", [])[-12:]
    if not rows:
        print("model> No history yet.")
        return
    for row in rows:
        event = row.get("event", "event")
        when = str(row.get("time", ""))[11:19] or "--:--:--"
        if event == "chat":
            print(f"{when} you> {row.get('user', '')}")
            print(f"         model> {row.get('assistant', '')}")
        elif event == "learning_result":
            result = row.get("result", {})
            print(f"{when} learned> {row.get('kind')} · accepted={result.get('accepted')} · "
                  f"{short_hash(result.get('learned_state_hash_after') or result.get('adapter_hash_after'))}")
        else:
            print(f"{when} {event}> {json.dumps(row, sort_keys=True)[:240]}")


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
        print("Compsmart CLM · private learner, fresh conversation")
        print(f"Session expires at {session['expires_at']}.")
        print("Type /help for model proof, history, reload and privacy controls.")
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
            if message == "/help":
                print(HELP)
                continue
            if message == "/model":
                print_model(client.model())
                continue
            if message == "/status":
                print_session(client.session_status())
                continue
            if message == "/history":
                print_history(client.history())
                continue
            if message == "/verify":
                value = client.verify()
                print(f"model> {'PASS' if value.get('passed') else 'FAIL'} · "
                      f"{value.get('checked', 0)} commitments · {short_hash(value.get('state_commitment'))}")
                continue
            if message == "/reload":
                value = client.reload()
                print(f"model> {'PASS' if value.get('reloaded') else 'FAIL'} · learned state restored from disk")
                for line in value.get("trace", []):
                    print(f"       {line}")
                continue
            if message == "/new":
                session = create_session(client, learner_file, saved)
                saved = {"learner_token": session["learner_token"]}
                print(f"model> New conversation; learned state retained. Expires at {session['expires_at']}.")
                continue
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

