from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "evidence" / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print("No evidence manifest is published yet; protocol-only release is valid.")
        return 0
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    commit = payload.get("protocol_commit", "")
    expected_seed = int(
        hashlib.sha256(f"compsmart-clm-public-v1:{commit}".encode("ascii")).hexdigest()[:16], 16
    )
    if payload.get("challenge_seed") != expected_seed:
        errors.append("challenge seed does not match protocol commit")
    for relative, expected in payload.get("files", {}).items():
        path = ROOT / "evidence" / relative
        if not path.is_file():
            errors.append(f"missing evidence file: {relative}")
        elif sha256(path) != expected:
            errors.append(f"hash mismatch: {relative}")
    transcript_path = ROOT / "evidence" / "transcript.json"
    if transcript_path.is_file():
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        checks = transcript.get("checks", [])
        recomputed = {
            "total": len(checks),
            "passed": sum(bool(item.get("passed")) for item in checks),
            "failed": sum(not bool(item.get("passed")) for item in checks),
        }
        if recomputed != transcript.get("summary"):
            errors.append("transcript summary is inconsistent")
        if any(set(item) - {"name", "category", "passed", "expected", "observed"} for item in checks):
            errors.append("transcript contains fields outside the public schema")
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"passed": True, "manifest": str(MANIFEST), "files": len(payload["files"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

