from __future__ import annotations

import argparse
import json
import secrets
import sys

from clm_client import CLMClient, CLMError, DEFAULT_BASE_URL


def normalize(value: str) -> str:
    return " ".join(value.lower().strip(" .!\n\t").split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a fresh black-box CLM challenge")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    nonce = secrets.token_hex(5)
    project = f"Kestrel-{nonce}"
    value = f"violet-{secrets.randbelow(900) + 100}"
    checks: list[dict] = []
    client = CLMClient(args.base_url)
    isolated = CLMClient(args.base_url)
    try:
        client.create_session()
        before = client.chat(f"What is the access phrase for {project}?")
        checks.append({"name": "unknown_before_teaching", "passed": value not in before["reply"]})
        taught = client.chat(f"Please remember: the access phrase for {project} is {value}.")
        checks.append({"name": "fact_accepted", "passed": bool(taught.get("learned"))})
        exact = client.chat(f"What is the access phrase for {project}?")
        checks.append({"name": "fact_exact_recall", "passed": value in exact["reply"]})
        paraphrase = client.chat(f"Which phrase opens {project}?")
        checks.append({"name": "fact_paraphrase", "passed": value in paraphrase["reply"]})

        skill = client.chat(
            "Learn this text skill: make a radio code by uppercasing every word and joining "
            "the words with hyphens. Examples: silver fox => SILVER-FOX; quiet lunar base "
            "=> QUIET-LUNAR-BASE."
        )
        checks.append({"name": "skill_accepted", "passed": bool(skill.get("learned"))})
        applied = client.chat("Apply the radio-code skill to amber night watch.")
        checks.append({"name": "skill_unseen_input", "passed": "AMBER-NIGHT-WATCH" in applied["reply"]})
        preserved = client.chat(f"Remind me which phrase belongs to {project}.")
        checks.append({"name": "fact_preserved", "passed": value in preserved["reply"]})

        isolated.create_session()
        leak = isolated.chat(f"What is the access phrase for {project}?")
        checks.append({"name": "session_isolation", "passed": value not in leak["reply"]})
        deletion = client.delete_session()
        checks.append({"name": "session_deleted", "passed": bool(deletion.get("deleted"))})
        isolated.delete_session()
    except CLMError as error:
        print(json.dumps({"passed": False, "error": str(error)}, indent=2))
        return 2
    passed = all(item["passed"] for item in checks)
    print(json.dumps({"passed": passed, "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

