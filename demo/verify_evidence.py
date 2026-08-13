from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "manifest.json"
ADAPTER_MANIFEST = ROOT / "evidence" / "v2" / "manifest.json"
OBSERVABLE_MANIFEST = ROOT / "evidence" / "observable-v2" / "manifest.json"


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
    verified_files = len(payload["files"])
    if ADAPTER_MANIFEST.is_file():
        adapter = json.loads(ADAPTER_MANIFEST.read_text(encoding="utf-8"))
        adapter_commit = adapter.get("protocol_commit", "")
        adapter_seed = int(hashlib.sha256(
            f"compsmart-clm-adapter-v2:{adapter_commit}".encode("ascii")
        ).hexdigest()[:16], 16)
        if adapter.get("protected_seed") != adapter_seed:
            errors.append("adapter v2 protected seed does not match protocol commit")
        for relative, expected in adapter.get("files", {}).items():
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                errors.append(f"unsafe adapter evidence path: {relative}")
                continue
            path = ADAPTER_MANIFEST.parent / relative
            if not path.is_file():
                errors.append(f"missing adapter evidence file: {relative}")
            elif sha256(path) != expected:
                errors.append(f"adapter evidence hash mismatch: {relative}")
        transcript = json.loads((ADAPTER_MANIFEST.parent / "transcript.json").read_text(encoding="utf-8"))
        checks = transcript.get("checks", [])
        summary = {"total": len(checks), "passed": sum(bool(row.get("passed")) for row in checks),
                   "failed": sum(not bool(row.get("passed")) for row in checks)}
        if transcript.get("summary") != summary:
            errors.append("adapter transcript summary is inconsistent")
        metrics = json.loads((ADAPTER_MANIFEST.parent / "metrics.json").read_text(encoding="utf-8"))
        if metrics.get("overall_checks") != summary or metrics.get("outcome") != "null-result-not-deployed":
            errors.append("adapter null-result metrics are inconsistent")
        if transcript.get("passed") is not False or adapter.get("outcome") != "null-result-not-deployed":
            errors.append("adapter deployment gate outcome is inconsistent")
        verified_files += len(adapter.get("files", {}))
    if OBSERVABLE_MANIFEST.is_file():
        observable = json.loads(OBSERVABLE_MANIFEST.read_text(encoding="utf-8"))
        for relative, expected in observable.get("files", {}).items():
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                errors.append(f"unsafe observable evidence path: {relative}")
                continue
            path = OBSERVABLE_MANIFEST.parent / relative
            if not path.is_file():
                errors.append(f"missing observable evidence file: {relative}")
            elif sha256(path) != expected:
                errors.append(f"observable evidence hash mismatch: {relative}")
        verification = json.loads((OBSERVABLE_MANIFEST.parent / "verification.json").read_text(encoding="utf-8"))
        if not verification.get("passed") or not all(row.get("passed") for row in verification.get("checks", [])):
            errors.append("observable deployment verification did not pass")
        deployment = json.loads((OBSERVABLE_MANIFEST.parent / "deployment.json").read_text(encoding="utf-8"))
        if (deployment.get("build_id") != observable.get("build_id")
                or deployment.get("parameter_updating") is not False
                or deployment.get("retrieval_used") is not True):
            errors.append("observable deployment disclosure is inconsistent")
        verified_files += len(observable.get("files", {}))
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"passed": True, "manifests": [str(MANIFEST), str(ADAPTER_MANIFEST),
                                                     str(OBSERVABLE_MANIFEST)],
                      "files": verified_files}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
