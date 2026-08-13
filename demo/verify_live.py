from __future__ import annotations

import argparse
import json
import secrets
import sys
import time

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL


def normalize(value: str) -> str:
    return " ".join(value.lower().strip(" .!\n\t").split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a fresh black-box CLM challenge")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--request-interval",
        type=float,
        default=0.25,
        help="seconds between requests in one session (default: 0.25)",
    )
    args = parser.parse_args()
    nonce = secrets.token_hex(5)
    project = f"Kestrel-{nonce}"
    value = f"violet-{secrets.randbelow(900) + 100}"
    checks: list[dict] = []
    client = CLMClient(args.base_url)
    isolated = CLMClient(args.base_url)
    last_primary = 0.0

    def primary_chat(message: str) -> dict:
        nonlocal last_primary
        remaining = args.request_interval - (time.monotonic() - last_primary)
        if remaining > 0:
            time.sleep(remaining)
        result = client.chat(message)
        last_primary = time.monotonic()
        return result

    try:
        model = client.model()
        service = client.service_status()
        checks.append({"name": "model_manifest", "passed": (
            model.get("parameters", {}).get("total", 0) > 4_000_000_000
            and model.get("base_files_bytes", 0) > 7_000_000_000
            and model.get("parameter_updating") is False
            and model.get("retrieval_used") is True
        )})
        checks.append({"name": "runtime_status", "passed": (
            service.get("status") == "ok" and bool(service.get("gpu", {}).get("name"))
        )})
        initial_session = client.create_session()
        learner_token = initial_session["learner_token"]
        initial_state = client.session_status()["learned_state"]["sha256"]
        before = primary_chat(f"What is the access phrase for {project}?")
        checks.append({"name": "unknown_before_teaching", "passed": value not in before["reply"]})
        taught = primary_chat(f"Please remember: the access phrase for {project} is {value}.")
        checks.append({"name": "fact_accepted", "passed": bool(taught.get("learned"))})
        learned_state = client.session_status()["learned_state"]["sha256"]
        checks.append({"name": "learned_state_changed", "passed": learned_state != initial_state})
        exact = primary_chat(f"What is the access phrase for {project}?")
        checks.append({"name": "fact_exact_recall", "passed": value in exact["reply"]})
        paraphrase = primary_chat(f"Which phrase opens {project}?")
        checks.append({"name": "fact_paraphrase", "passed": value in paraphrase["reply"]})

        skill = primary_chat(
            "Learn this text skill: make a radio code by uppercasing every word and joining "
            "the words with hyphens. Examples: silver fox => SILVER-FOX; quiet lunar base "
            "=> QUIET-LUNAR-BASE."
        )
        checks.append({"name": "skill_accepted", "passed": bool(skill.get("learned"))})
        applied = primary_chat("Apply the radio-code skill to amber night watch.")
        checks.append({"name": "skill_unseen_input", "passed": "AMBER-NIGHT-WATCH" in applied["reply"]})
        # Reuse the canonical question here so preservation is not confounded
        # with a second, separately uncertain paraphrase-routing decision.
        preserved = primary_chat(f"What is the access phrase for {project}?")
        checks.append({"name": "fact_preserved", "passed": value in preserved["reply"]})

        client.delete_session()
        client.create_session(learner_token=learner_token)
        fresh_session = primary_chat(f"What is the access phrase for {project}?")
        checks.append(
            {"name": "fresh_session_recall", "passed": value in fresh_session["reply"]}
        )
        reloaded = client.reload()
        checks.append({"name": "disk_reload", "passed": (
            bool(reloaded.get("reloaded"))
            and reloaded.get("adapter_hash_before") == reloaded.get("adapter_hash_after")
        )})
        post_reload = primary_chat(f"What is the access phrase for {project}?")
        checks.append({"name": "post_reload_recall", "passed": value in post_reload["reply"]})
        verified = client.verify()
        checks.append({"name": "commitment_replay", "passed": bool(verified.get("passed"))})
        history = client.history()
        checks.append({"name": "prompt_history", "passed": any(
            row.get("event") == "chat" and row.get("user")
            for row in history.get("events", [])
        )})

        isolated.create_session()
        leak = isolated.chat(f"What is the access phrase for {project}?")
        checks.append({"name": "learner_isolation", "passed": value not in leak["reply"]})
        deletion = client.delete_learner()
        checks.append({"name": "learner_deleted", "passed": bool(deletion.get("deleted"))})
        isolated.delete_learner()
    except CLMError as error:
        print(json.dumps({"passed": False, "error": str(error)}, indent=2))
        return 2
    passed = all(item["passed"] for item in checks)
    print(json.dumps({"passed": passed, "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
