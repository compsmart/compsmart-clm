from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def recompute_metrics(transcript: dict) -> dict:
    checks = transcript.get("checks", [])
    fact_lessons = [item for item in checks if item["category"] == "learning" and item["name"].startswith("fact-")]
    skill_lessons = [item for item in checks if item["category"] == "learning" and item["name"].startswith("skill-")]
    accepted_skill_ids = {
        item["name"].split("-")[1] for item in skill_lessons if item["passed"]
    }
    generalization = [item for item in checks if item["category"] == "generalization"]
    accepted_generalization = [
        item
        for item in generalization
        if item["name"].startswith("fact-")
        or item["name"].split("-")[1] in accepted_skill_ids
    ]
    preservation = [item for item in checks if item["category"] == "preservation"]
    restart = [item for item in checks if item["category"] == "restart"]
    accepted_restart = [
        item
        for item in restart
        if item["name"].startswith("fact-")
        or item["name"].split("-")[1] in accepted_skill_ids
    ]
    return {
        "overall_checks": {
            "passed": sum(bool(item["passed"]) for item in checks),
            "total": len(checks),
        },
        "lesson_acquisition": {
            "facts_accepted": sum(bool(item["passed"]) for item in fact_lessons),
            "facts_attempted": len(fact_lessons),
            "skills_accepted": sum(bool(item["passed"]) for item in skill_lessons),
            "skills_attempted": len(skill_lessons),
        },
        "retention": {
            "sequential_preservation_passed": sum(bool(item["passed"]) for item in preservation),
            "sequential_preservation_total": len(preservation),
            "observed_regressions": sum(not bool(item["passed"]) for item in preservation),
            "accepted_lessons_after_fresh_process_passed": sum(bool(item["passed"]) for item in accepted_restart),
            "accepted_lessons_after_fresh_process_total": len(accepted_restart),
        },
        "generalization": {
            "accepted_lessons_passed": sum(bool(item["passed"]) for item in accepted_generalization),
            "accepted_lessons_total": len(accepted_generalization),
            "all_requested_probes_passed": sum(bool(item["passed"]) for item in generalization),
            "all_requested_probes_total": len(generalization),
        },
    }


def compare_metrics(published: dict, recomputed: dict, errors: list[str]) -> None:
    for section, fields in recomputed.items():
        actual_section = published.get(section, {})
        for field, expected in fields.items():
            if actual_section.get(field) != expected:
                errors.append(f"metrics mismatch: {section}.{field}")


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
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"unsafe evidence path: {relative}")
            continue
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
        metrics_path = ROOT / "evidence" / "metrics.json"
        if metrics_path.is_file():
            published_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            compare_metrics(published_metrics, recompute_metrics(transcript), errors)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"passed": True, "manifest": str(MANIFEST), "files": len(payload["files"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
